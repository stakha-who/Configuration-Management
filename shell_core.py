import os
import re
import datetime
from config import Config


class ShellCore:
    """Ядро оболочки - содержит всю логику командной строки"""

    # Конструктор
    def __init__(self, vfs, config):
        self.vfs = vfs              # сохраняет ссылку на vfs для доступа к файловой 
        self.config = config
        self.commands = {           # список команд
            'echo': self.cmd_echo,
            'ls': self.cmd_ls,
            'cd': self.cmd_cd,
            'exit': self.cmd_exit,
            'find': self.cmd_find,
            'rev': self.cmd_rev,
            'who': self.cmd_who,
            'mkdir': self.cmd_mkdir
        }

    def _expand_env_vars(self, text):
        """Раскрытие переменных окружения в формате $VAR или ${VAR}"""

        def replace_var(match):
            var_name = match.group(1) or match.group(2)  # группа 1 - $HOME, группа 2 - ${HOME}; берем что-то одно
            return os.getenv(var_name, '')

        # Регуляное выражение для обработки $VAR или ${VAR}
        pattern = r'\$([a-zA-Z_][a-zA-Z0-9_]*)|\$\{([a-zA-Z_][a-zA-Z0-9_]*)\}'
        return re.sub(
            pattern,        # шаблон, вхождение которого нужно заменить
            replace_var,    # функция, производящая замену
            text            # строка, для которой производится замена
        )

    def parse_command(self, input_line):
        """Парсер команд"""

        if not input_line.strip():
            return "", []

        # Раскрываем переменные окружения
        expanded_input = self._expand_env_vars(input_line)

        # Разбиваем на команду и аргументы
        parts = expanded_input.split()
        command = parts[0] if parts else ""
        args = parts[1:] if len(parts) > 1 else []

        return command, args

    def execute(self, command, args):
        """Выполнение команды"""

        if command in self.commands:
            try:
                return self.commands[command](args)
            except Exception as e:
                return f"Ошибка выполнения команды {command}: {str(e)}"
        elif command:
            return f"Команда не найдена: {command}"
        else:
            return ""


    """Область разработки команд"""

    def cmd_ls(self, args):
        """Команда ls - список файлов и директорий"""

        path = args[0] if args else None

        success, result = self.vfs.list_directory(path)
        if success:
            return result
        else:
            return f"ls: {result}"

    def cmd_cd(self, args):
        """Команда cd - смена директории"""

        target = args[0] if args else "/"

        success, result = self.vfs.change_directory(target)
        if success:
            return result
        else:
            return f"cd: {result}"

    def cmd_exit(self, args):
        """Команда exit - завершает программу"""

        return "EXIT"
    
    def cmd_echo(self, args):
        """Команда echo - вывод текста в консоль"""

        if not args:
            return ""

        text = " ".join(args)

        # Раскрываем переменные окружения
        expanded_text = self._expand_env_vars(text)
        return expanded_text
    
    def cmd_find(self, args):
        """Команда find - поиск файлов и директорий по имени"""

        if not args:
            return "find: отсутствуют аргументы. Использование: find <путь> -name <шаблон>"

        # Базовая реализация: find <путь> -name <шаблон>
        if len(args) < 3 or args[1] != "-name":
            return "find: поддерживается только форма: find <путь> -name <шаблон>"

        search_path = args[0]
        pattern = args[2]

        results = self.vfs.find_files(search_path, pattern)
        if results is None:
            return f"find: {search_path}: директория не найдена"

        if not results:
            return ""  # ничего не найдено

        return '\n'.join(results)
    
    def cmd_rev(self, args):
        """Команда rev - переворачивает строки или содержимое файла"""

        if not args:
            return "rev: отсутствуют аргументы. Использование: rev <файл> или rev <текст>"

        # Если первый аргумент существует как файл в VFS, читаем его содержимое
        filename = args[0]
        file_node = self.vfs.get_file_content(filename)

        if file_node is not None and file_node.type == "file":
            # Работа с файлом
            content = file_node.content or ""
            if not content:
                return ""  # пустой файл

            # Переворачиваем каждую строку отдельно
            lines = content.split('\n')
            reversed_lines = [line[::-1] for line in lines]  # переворачиваем каждую строку
            return '\n'.join(reversed_lines)
        else:
            # Работа с текстом из аргументов
            text = " ".join(args)
            # Переворачиваем весь текст
            return text[::-1]
    
    def cmd_who(self, args):
        """Команда who - отображает информацию о текущих пользователях"""
        
        # В нашей виртуальной системе имитируем информацию о пользователях
        # В реальной системе эта команда показывает кто залогинен в системе
        
        current_user = "user"
        current_path = self.vfs.get_current_path()
        
        # Создаем имитацию вывода команды who
        who_info = f"""
    Пользователь    TTY         Время входа
    {current_user}          pts/0       {self._get_current_time()}
    {current_user}          pts/1       {self._get_current_time()}

    Всего пользователей в системе: 2
    Текущий пользователь: {current_user}
    Текущая директория: {current_path}
    """
        return who_info.strip()
    
    def _get_current_time(self):
        """Вспомогательная функция для получения текущего времени (имитация)"""

        now = datetime.datetime.now()
        return now.strftime("%Y-%m-%d %H:%M:%S")
    
    def cmd_mkdir(self, args):
        """Команда mkdir - создание директорий"""

        if not args:
            return "mkdir: отсутствует аргумент - имя директории"

        success, message = self.vfs.create_directory(args[0])
        return message if success else f"mkdir: {message}"