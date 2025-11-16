import argparse
from typing import Optional, Dict, Any


class Config:
    """Класс для хранения и валидации конфигурации приложения"""

    def __init__(self):
        self.package_name: Optional[str] = None
        self.repo_url: Optional[str] = None
        self.test_mode: bool = False
        self.version: Optional[str] = None
        self.output_file: str = "dependency_graph.png"
        self.max_depth: Optional[int] = None
        self.ascii_mode: bool = False
        self.filter_substring: Optional[str] = None

    def validate(self) -> None:
        """Валидация параметров конфигурации"""

        if not self.package_name:
            raise ValueError("Имя пакета обязательно для указания")

        if not self.repo_url:
            raise ValueError("URL репозитория или путь к файлу обязателен")

        if self.version and not self._is_valid_version(self.version):
            raise ValueError(f"Некорректный формат версии: {self.version}")

        if self.max_depth is not None:
            if not isinstance(self.max_depth, int) or self.max_depth < 1:
                raise ValueError("Максимальная глубина должна быть положительным целым числом")

        if self.output_file and not self._is_valid_filename(self.output_file):
            raise ValueError(f"Некорректное имя файла: {self.output_file}")

    def _is_valid_version(self, version: str) -> bool:
        import re
        pattern = r"^[a-zA-Z0-9._-]+$"
        return bool(re.match(pattern, version))

    def _is_valid_filename(self, filename: str) -> bool:
        forbidden = ['<', '>', ':', '"', '|', '?', '*', '\\', '/']
        return filename and isinstance(filename, str) and not any(c in filename for c in forbidden)

    def to_dict(self) -> Dict[str, Any]:
        """Возвращает конфигурацию для вывода"""

        return {
            "package_name": self.package_name,
            "repo_url": self.repo_url,
            "test_mode": self.test_mode,
            "version": self.version if self.version else "latest",
            "output_file": self.output_file,
            "ascii_mode": self.ascii_mode,
            "max_depth": self.max_depth if self.max_depth else "unlimited",
            "filter_substring": self.filter_substring if self.filter_substring else "none",
        }

    def is_test_mode(self) -> bool:
        return self.test_mode


def parse_arguments() -> Config:
    """Парсинг аргументов командной строки"""

    parser = argparse.ArgumentParser(
        description="Визуализация графа зависимостей (вариант 2, этап 1)"
    )

    parser.add_argument("-p", "--package", type=str, required=True,
                        help="Имя анализируемого пакета")
    parser.add_argument("-r", "--repo", type=str, required=True,
                        help="URL репозитория или путь к файлу тестового репозитория")
    parser.add_argument("-t", "--test-mode", action="store_true",
                        help="Режим работы с тестовым репозиторием")
    parser.add_argument("-v", "--version", type=str,
                        help="Версия пакета")
    parser.add_argument("-o", "--output", type=str, default="dependency_graph.png",
                        help="Имя создаваемого PNG-файла с графом")
    parser.add_argument("-d", "--max-depth", type=int,
                        help="Максимальная глубина анализа зависимостей")
    parser.add_argument("-a", "--ascii", action="store_true",
                        help="Режим вывода зависимостей в виде ASCII-дерева")
    parser.add_argument("-f", "--filter", type=str,
                        help="Подстрока для фильтрации пакетов")

    args = parser.parse_args()

    cfg = Config()
    cfg.package_name = args.package
    cfg.repo_url = args.repo
    cfg.test_mode = args.test_mode
    cfg.version = args.version
    cfg.output_file = args.output
    cfg.max_depth = args.max_depth
    cfg.ascii_mode = args.ascii
    cfg.filter_substring = args.filter

    cfg.validate()
    return cfg


def print_config(config: Config):
    """Печать конфигурации в формате ключ-значение"""

    print("\nТекущая конфигурация:")
    print("------------------------------")

    for key, value in config.to_dict().items():
        print(f"{key}: {value}")

    print("------------------------------")
