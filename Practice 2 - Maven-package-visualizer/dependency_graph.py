from collections import deque
from typing import Dict, List, Optional, Any, Set
import sys


def build_dependency_graph_recursive_bfs(
    repo: Any,
    root_package: str,
    version: str,
    max_depth: Optional[int] = None,
    filter_substring: Optional[str] = None
) -> Dict[str, List[str]]:
    """Рекурсивная реализация BFS для построения графа зависимостей"""

    graph: Dict[str, List[str]] = {}
    visited: Set[str] = set()

    def bfs_step(current_package: str, current_version: str, current_depth: int):
        if max_depth is not None and current_depth > max_depth:
            return

        node_key = f"{current_package}:{current_version}"
        if node_key in visited:
            return
        visited.add(node_key)

        try:
            raw_deps = repo.get_dependencies(current_package, current_version)
        except Exception as e:
            # Логируем, но продолжаем
            sys.stderr.write(f"Предупреждение: не удалось получить зависимости для {node_key}: {e}\n")
            graph[node_key] = []
            return

        # Фильтрация по подстроке
        if filter_substring:
            raw_deps = [d for d in raw_deps if filter_substring not in d]

        graph[node_key] = raw_deps

        # Извлекаем зависимости для следующего уровня
        next_level = []
        for dep in raw_deps:
            parts = dep.split(':', 2)
            if len(parts) < 3:
                continue
            dep_pkg = f"{parts[0]}:{parts[1]}"
            dep_ver = parts[2]
            next_level.append((dep_pkg, dep_ver))

        # Имитация BFS через очередь, но внутри рекурсивной функции
        queue = deque(next_level)
        while queue:
            pkg, ver = queue.popleft()
            child_key = f"{pkg}:{ver}"
            if child_key not in visited:
                # Рекурсивный вызов для следующего уровня глубины
                bfs_step(pkg, ver, current_depth + 1)

    bfs_step(root_package, version, 1)
    return graph