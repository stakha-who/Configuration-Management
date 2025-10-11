import socket
import csv
import os
import base64


class VFSNode:
    """Узел виртуальной файловой системы (файл или директория)"""

    def __init__(self, name, node_type="dir", content=""):
        self.name = name
        self.type = node_type                               # "dir" или "file"
        self.content = content
        self.children = {} if node_type == "dir" else None  # дочерние узлы могут быть только у директорий
        self.parent = None


class VFS:
    """Виртуальная файловая система (в разработке)"""

    def __init__(self):
        self.root = VFSNode("", "dir")
        self.current_node = self.root
        self.name = f"Эмулятор - {socket.gethostname()}"
        self._build_default_structure()  # структура vfs по умолчанию

    def _build_default_structure(self):
        """Создает минимальную структуру VFS по умолчанию"""

        # Создаем базовую структуру Unix-подобной системы
        home_dir = self._add_child(self.root, "home", "dir")
        self._add_child(home_dir, "user", "dir")
        self._add_child(self.root, "etc", "dir")
        self._add_child(self.root, "var", "dir")
        self._add_child(self.root, "tmp", "dir")

        # Устанавливаем текущую директорию в /home/user
        self.current_node = home_dir.children["user"]

    def _add_child(self, parent, name, node_type="dir", content=""):
        """Добавляет дочерний узел"""

        node = VFSNode(name, node_type, content)
        node.parent = parent
        if parent.children is not None:
            parent.children[name] = node
        return node

    def _resolve_path(self, path):
        """Разрешает путь к узлу VFS"""

        if path.startswith("/"):
            # Абсолютный путь
            current = self.root
            path_parts = path.split("/")[1:]  # убираем пустой первый элемент
        else:
            # Относительный путь
            current = self.current_node
            path_parts = path.split("/")

        for part in path_parts:
            if not part or part == ".":
                continue
            elif part == "..":
                if current.parent:
                    current = current.parent
            else:
                if (current.children and
                        part in current.children and
                        current.children[part].type == "dir"):
                    current = current.children[part]
                else:
                    # Проверяем, может это файл в текущей директории
                    if (current.children and part in current.children):
                        return current.children[part]
                    return None

        return current

    def load_from_csv(self, csv_path):
        """Загружает VFS из CSV файла"""

        if not os.path.exists(csv_path):
            raise FileNotFoundError(f"CSV файл не найден: {csv_path}")

        try:
            # Очищаем текущую структуру
            self.root = VFSNode("", "dir")
            self.current_node = self.root

            with open(csv_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                
                for row in reader:
                    self._process_csv_row(row)

            # Возвращаемся в корневую директорию
            self.current_node = self.root

        except Exception as e:
            raise ValueError(f"Ошибка загрузки CSV: {str(e)}")

    def _process_csv_row(self, row):
        """Обрабатывает строку CSV и создает соответствующий узел в VFS"""
        
        try:
            # Проверяем обязательные поля и обрабатываем None значения
            if 'path' not in row or 'type' not in row or 'name' not in row:
                print(f"Пропуск строки с отсутствующими обязательными полями: {row}")
                return
            
            # Безопасно обрабатываем значения, которые могут быть None
            path = row['path'] or ''
            node_type = row['type'] or ''
            name = row['name'] or ''
            content = row.get('content', '') or ''
            encoding = row.get('encoding', '') or ''
    
            path = path.strip()
            node_type = node_type.strip()
            name = name.strip()
            content = content.strip()
            encoding = encoding.strip()

            print(f"Обработка: path='{path}', type='{node_type}', name='{name}', encoding='{encoding}'")

            # Обрабатываем кодировку base64
            if encoding == 'base64':
                try:
                    content = base64.b64decode(content).decode('utf-8')
                    print(f"Декодировано base64 содержимое: {content}")
                except Exception as e:
                    content = f"Ошибка декодирования base64: {str(e)}"
                    print(f"Ошибка декодирования base64: {e}")
                else:
                    # Обрабатываем экранированные символы в обычном содержимом
                    if content:
                        content = content.replace('\\n', '\n').replace('\\t', '\t')

            # Разбираем путь
            path_parts = [p for p in path.split('/') if p]  # Убираем пустые части
            
            print(f"Разобранный путь: {path_parts}")
            
            # Начинаем с корневой директории
            current_node = self.root
            
            # Создаем все промежуточные директории
            for part in path_parts:
                if current_node.children is None:
                    current_node.children = {}
                    
                if part not in current_node.children:
                    # Создаем промежуточную директорию
                    print(f"Создание директории: {part}")
                    new_dir = VFSNode(part, "dir")
                    new_dir.parent = current_node
                    current_node.children[part] = new_dir
                    current_node = new_dir
                else:
                    current_node = current_node.children[part]
                    if current_node.type != "dir":
                        # Если нашли файл вместо директории, это ошибка в структуре
                        error_msg = f"Невозможно создать путь {path}: {part} является файлом"
                        print(f"Ошибка: {error_msg}")
                        raise ValueError(error_msg)

            # Создаем конечный узел
            if current_node.children is None:
                current_node.children = {}
                
            if name in current_node.children:
                # Обновляем существующий узел
                existing_node = current_node.children[name]
                if existing_node.type != node_type:
                    error_msg = f"Конфликт типов для {path}/{name}"
                    print(f"Ошибка: {error_msg}")
                    raise ValueError(error_msg)
                existing_node.content = content
                print(f"Обновлен существующий узел: {name}")
            else:
                # Создаем новый узел
                print(f"Создание нового узла: {name} типа {node_type}")
                new_node = VFSNode(name, node_type, content)
                new_node.parent = current_node
                current_node.children[name] = new_node
                
        except Exception as e:
            print(f"Ошибка обработки строки CSV {row}: {e}")
            raise

    def get_current_path(self):
        """Возвращает текущий путь в VFS"""

        path_parts = []
        node = self.current_node

        # Поднимаемся вверх по иерархии до корня
        while node and node.parent:
            path_parts.insert(0, node.name)
            node = node.parent

        return "/" + "/".join(path_parts) if path_parts else "/"

    def change_directory(self, path):
        """Изменяет текущую директорию. Алгоритм команды cd"""

        if not path:
            return False, "Путь не указан"

        target_node = self._resolve_path(path)
        if not target_node:
            return False, f"Директория не найдена: {path}"

        if target_node.type != "dir":
            return False, f"Не директория: {path}"

        self.current_node = target_node
        return True, f"Переход в {self.get_current_path()}"

    def list_directory(self, path=None):
        """Список содержимого директории. Алгоритм команды ls"""

        if path:
            target_node = self._resolve_path(path)
            if not target_node:
                return False, f"Директория не найдена: {path}"
        else:
            target_node = self.current_node

        if target_node.type != "dir":
            return False, f"Не директория: {path if path else self.get_current_path()}"

        if not target_node.children:
            return True, "Директория пуста"

        items = list(target_node.children.keys())
        return True, "\n".join(sorted(items))