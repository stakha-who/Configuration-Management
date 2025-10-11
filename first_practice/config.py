import argparse
import os
import sys


class Config:
    """Конфигурация командной строки - управляет настройками эмулятора"""

    def __init__(self):
        self.vfs_path = None        # путь к физическому расположению VFS
        self.script_path = None     # путь к стартовому скрипту
        self.raw_arguments = []     # аргументы при запуске

    def parse_arguments(self):
        """Парсинг аргументов командной строки"""

        parser = argparse.ArgumentParser(
            description='Unix-like command line emulator',
            epilog='Пример: python main.py --vfs ./vfs.xml --script ./startup.vsh'
        )

        # Добавляем аргументы командной строки
        parser.add_argument(
            '--vfs',
            dest='vfs_path',
            help='Путь к CSV файлу виртуальной файловой системы'
        )

        parser.add_argument(
            '--script',
            dest='script_path',
            help='Путь к стартовому скрипту для выполнения'
        )

        # Сохраняем исходные аргументы (кроме имени скрипта - main.py)
        self.raw_arguments = sys.argv[1:]

        # Парсим аргументы
        args = parser.parse_args()

        # Преобразуем относительные пути в абсолютные
        if args.script_path:
            self.script_path = self._resolve_path(args.script_path)

        if args.vfs_path:
            self.vfs_path = self._resolve_path(args.vfs_path)

    def _resolve_path(self, path):
        """Преобразует относительный путь в абсолютный относительно расположения проекта"""

        # Если путь уже абсолютный - возвращаем как есть
        if os.path.isabs(path):
            return path

        # Получаем абсолютный путь относительно текущей рабочей директории
        abs_path = os.path.abspath(path)

        # Проверяем существует ли файл по этому пути
        if os.path.exists(abs_path):
            return abs_path

        # Если файл не найден, пытаемся найти относительно директории проекта
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        project_path = os.path.join(project_root, path)

        if os.path.exists(project_path):
            return project_path

        # Если файл все равно не найден, возвращаем исходный путь (для генерации понятной ошибки)
        return abs_path

    def get_startup_parameters(self):
        """Возвращает строку с параметрами запуска"""

        if not self.raw_arguments:
            return "нет параметров"

        return " ".join(self.raw_arguments)