import urllib.request
import urllib.error
import xml.etree.ElementTree as ET
import re
from typing import List, Tuple, Optional


class MavenRepository:
    """Класс для получения зависимостей из Maven Central"""

    def __init__(self, repo_url: str):
        self.repo_url = repo_url.rstrip('/')

    def get_dependencies(self, package_name: str, version: str) -> List[str]:
        """Возвращает список зависимостей в формате ['group:artifact:version', ...]"""
        
        group, artifact = self._parse_package_name(package_name)
        pom_content = self._fetch_pom(group, artifact, version)
        return self._extract_dependencies(pom_content)

    def _parse_package_name(self, package: str) -> Tuple[str, str]:
        if ':' not in package:
            raise ValueError(f"Неверный формат имени пакета: {package}. Ожидается groupId:artifactId")
        return package.split(':', 1)

    def _fetch_pom(self, group_id: str, artifact_id: str, version: str) -> str:
        group_path = group_id.replace('.', '/')
        pom_url = f"{self.repo_url}/{group_path}/{artifact_id}/{version}/{artifact_id}-{version}.pom"
        try:
            with urllib.request.urlopen(pom_url) as response:
                return response.read().decode('utf-8')
        except urllib.error.HTTPError as e:
            if e.code == 404:
                raise ValueError(f"POM-файл для {group_id}:{artifact_id}:{version} не найден")
            else:
                raise ConnectionError(f"Ошибка HTTP {e.code} при доступе к {pom_url}")
        except urllib.error.URLError as e:
            raise ConnectionError(f"Ошибка сети: {e.reason}")

    def _extract_dependencies(self, pom_content: str) -> List[str]:
        try:
            root = ET.fromstring(pom_content)
            ns_match = re.match(r'\{.*\}', root.tag)
            ns_uri = ns_match.group(0)[1:-1] if ns_match else ''
            ns = {'m': ns_uri} if ns_uri else {}

            deps = []
            deps_elem = root.find('.//m:dependencies', ns) if ns_uri else root.find('.//dependencies')
            if deps_elem is not None:
                for dep in deps_elem.findall('m:dependency', ns) if ns_uri else deps_elem.findall('dependency'):
                    gid = dep.find('m:groupId', ns) if ns_uri else dep.find('groupId')
                    aid = dep.find('m:artifactId', ns) if ns_uri else dep.find('artifactId')
                    ver = dep.find('m:version', ns) if ns_uri else dep.find('version')

                    if gid is not None and aid is not None:
                        group = gid.text.strip()
                        artifact = aid.text.strip()
                        version = ver.text.strip() if ver is not None and ver.text else "latest"
                        deps.append(f"{group}:{artifact}:{version}")
            return deps
        except ET.ParseError:
            # Если не получилось, пробуем регулярками
            deps = []
            dep_blocks = re.findall(r'<dependency>(.*?)</dependency>', pom_content, re.DOTALL)
            for block in dep_blocks:
                gid = re.search(r'<groupId>(.*?)</groupId>', block)
                aid = re.search(r'<artifactId>(.*?)</artifactId>', block)
                ver = re.search(r'<version>(.*?)</version>', block)
                if gid and aid:
                    group = gid.group(1).strip()
                    artifact = aid.group(1).strip()
                    version = ver.group(1).strip() if ver else "latest"
                    deps.append(f"{group}:{artifact}:{version}")
            return deps