from typing import List, Tuple, Dict, Set, Optional
from collections import deque
import sys
import os
from maven_repository import MavenRepository
from test_repository import TestRepository


def make_node_id(group: str, artifact: str, version: Optional[str]) -> str:
    v = version if version else "unknown"
    return f"{group}:{artifact}:{v}"


def split_package_name(pkg: str) -> Tuple[str, str]:
    """Разделить 'group:artifact' на две части
       Если формат простой ('A'), используем group=artifact=pkg"""
       
    if ':' not in pkg:
        return pkg, pkg
    group, artifact = pkg.split(':', 1)
    return group, artifact


class DependencyGraph:
    """Класс для построения и анализа графа зависимостей с поддержкой фильтрации и рекурсивного BFS"""

    def __init__(self, repo_url: str, test_mode: bool = False):
        self.repo_url = repo_url
        self.test_mode = test_mode
        self.graph: Dict[str, List[str]] = {}
        self.meta: Dict[str, Tuple[str, str, str]] = {}
        self.visited: Set[str] = set()
        if test_mode:
            self.repo_client = TestRepository(repo_url)
        else:
            self.repo_client = MavenRepository(repo_url)

    def build_graph(
        self,
        root_package: str,
        version: Optional[str] = None,
        max_depth: Optional[int] = None,
        filter_substring: Optional[str] = None
    ) -> None:
        """Построение графа зависимостей рекурсивным BFS (уровневый обход с рекурсией)"""
        root_group, root_artifact = split_package_name(root_package)
        root_id = make_node_id(root_group, root_artifact, version)
        self.meta[root_id] = (root_group, root_artifact, version or "unknown")
        self.visited.clear()
        self.graph.clear()

        def bfs_recursive(queue: deque, current_depth: int):
            if not queue or (max_depth is not None and current_depth > max_depth):
                return

            next_queue = deque()
            while queue:
                node_id = queue.popleft()
                if node_id in self.visited:
                    continue
                self.visited.add(node_id)

                # Получаем group/artifact/version
                group, artifact, ver = self.meta[node_id]
                pkg_for_client = f"{group}:{artifact}"
                try:
                    raw_deps = self.repo_client.get_dependencies(pkg_for_client, ver)
                except Exception as e:
                    sys.stderr.write(f"Предупреждение: зависимости для {node_id} недоступны: {e}\n")
                    self.graph[node_id] = []
                    continue

                # Преобразуем зависимости и применяем фильтрацию
                filtered_deps = []
                for dep_group, dep_artifact, dep_version in raw_deps:
                    dep_full = f"{dep_group}:{dep_artifact}:{dep_version}"
                    if filter_substring and filter_substring in dep_full:
                        continue
                    filtered_deps.append((dep_group, dep_artifact, dep_version))

                # Сохраняем зависимости в граф
                children_ids = []
                for g, a, v in filtered_deps:
                    child_id = make_node_id(g, a, v)
                    children_ids.append(child_id)
                    if child_id not in self.meta:
                        self.meta[child_id] = (g, a, v)
                self.graph[node_id] = children_ids

                # Готовим следующий уровень
                for child_id in children_ids:
                    if child_id not in self.visited:
                        next_queue.append(child_id)

            # Рекурсивный вызов для следующего уровня
            bfs_recursive(next_queue, current_depth + 1)

        bfs_recursive(deque([root_id]), 1)

    def get_load_order(self, root_package: str, version: Optional[str] = None) -> List[str]:
        """Возвращает порядок загрузки зависимостей (уровневый обход графа без повторов)."""
        root_group, root_artifact = split_package_name(root_package)
        root_id = make_node_id(root_group, root_artifact, version)

        # Попытка найти корень в графе
        if root_id not in self.graph:
            candidates = [n for n in self.graph if n.startswith(f"{root_group}:{root_artifact}:")]
            if not candidates:
                raise ValueError("Корневой пакет не найден в графе зависимостей")
            root_id = candidates[0]

        visited = set()
        queue = deque([root_id])
        load_order = []

        while queue:
            node = queue.popleft()
            if node in visited:
                continue
            visited.add(node)
            load_order.append(node)

            for child in self.graph.get(node, []):
                if child not in visited:
                    queue.append(child)

        return load_order