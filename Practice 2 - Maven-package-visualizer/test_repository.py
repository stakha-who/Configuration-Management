import os
from typing import List


class TestRepository:
    """Загружает тестовый репозиторий из .txt-файла"""

    def __init__(self, file_path: str):
        if not os.path.isfile(file_path):
            raise ValueError(f"Файл не найден: {file_path}")
        self.dependencies = self._load_from_file(file_path)

    def _load_from_file(self, path: str) -> dict:
        deps = {}
        with open(path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                if '->' in line:
                    pkg, dep_list = line.split('->', 1)
                    pkg = pkg.strip()
                    dep_names = [d.strip() for d in dep_list.split(',') if d.strip()]
                    deps[pkg] = [f"{d}:{d}:1.0.0" for d in dep_names]  # формат: group:artifact:version
        return deps

    def get_dependencies(self, package_name: str, version: str = "1.0.0") -> List[str]:
        # Поддержка как "A", так и "A:A"
        if package_name in self.dependencies:
            return self.dependencies[package_name]
        # Если передано "A:B", пробуем "A"
        if ':' in package_name:
            simple = package_name.split(':', 1)[0]
            if simple in self.dependencies:
                return self.dependencies[simple]
        raise ValueError(f"Пакет {package_name} не найден в тестовом репозитории")