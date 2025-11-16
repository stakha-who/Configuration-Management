import os
import requests
import xml.etree.ElementTree as ET


def load_repository_local(path: str) -> dict:
    """Загрузка репозитория в режиме --test-mode (локальные файлы)."""
    if not os.path.isdir(path):
        raise ValueError(f"Путь '{path}' не является директорией")

    repo = {}

    for filename in os.listdir(path):
        full_path = os.path.join(path, filename)
        if not os.path.isfile(full_path):
            continue

        with open(full_path, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f.readlines()]

        package = None
        depends = []

        for line in lines:
            if line.startswith("package:"):
                package = line.split(":", 1)[1].strip()
            elif line.startswith("- "):
                depends.append(line[2:].strip())

        if package:
            repo[package] = depends

    return repo


def parse_package_name(package: str):
    """Разделяет org.apache:commons-lang3 → (groupId, artifactId)."""
    if ":" not in package:
        raise ValueError("Неверный формат имени пакета. Ожидается groupId:artifactId")

    group_id, artifact_id = package.split(":", 1)
    return group_id, artifact_id


def build_pom_url(repo_url: str, group: str, artifact: str, version: str) -> str:
    """Строит URL pom-файла."""
    group_path = group.replace(".", "/")
    return f"{repo_url.rstrip('/')}/{group_path}/{artifact}/{version}/{artifact}-{version}.pom"


def download_pom(url: str) -> str:
    """Скачивает pom.xml как текст."""
    r = requests.get(url, timeout=10)
    if r.status_code != 200:
        raise ValueError(f"Не удалось скачать pom.xml по адресу: {url}")
    return r.text


def parse_dependencies_from_pom(pom_text: str) -> list:
    """Извлекает список зависимостей из pom.xml."""
    root = ET.fromstring(pom_text)

    deps = []
    ns = {"m": "http://maven.apache.org/POM/4.0.0"}

    for dep in root.findall(".//m:dependency", ns):
        gid = dep.find("m:groupId", ns)
        aid = dep.find("m:artifactId", ns)
        ver = dep.find("m:version", ns)

        if gid is None or aid is None:
            continue

        group = gid.text.strip()
        artifact = aid.text.strip()
        version = ver.text.strip() if ver is not None else "LATEST"

        deps.append(f"{group}:{artifact}:{version}")

    return deps


def get_dependencies_http(package: str, repo_url: str, version: str):
    """Получает зависимости реального пакета из Maven Central."""
    group, artifact = parse_package_name(package)
    pom_url = build_pom_url(repo_url, group, artifact, version)
    pom_text = download_pom(pom_url)
    return parse_dependencies_from_pom(pom_text)


def recursive_collect_http(package: str, repo_url: str, version: str, max_depth: int | None):
    """Рекурсивный сбор зависимостей через HTTP."""
    result = {}
    visited = set()

    def dfs(pkg, ver, depth):
        if pkg in visited:
            return
        visited.add(pkg)

        deps = get_dependencies_http(pkg, repo_url, ver)
        result[f"{pkg}:{ver}"] = deps

        if max_depth is not None and depth >= max_depth:
            return

        for full_dep in deps:
            parts = full_dep.split(":")
            if len(parts) == 3:
                dep_pkg = parts[0] + ":" + parts[1]
                dep_ver = parts[2]
                dfs(dep_pkg, dep_ver, depth + 1)

    dfs(package, version, 1)
    return result
