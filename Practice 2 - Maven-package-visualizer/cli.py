import sys
from config import parse_arguments, print_config
from maven_repository import MavenRepository
from test_repository import TestRepository
from dependency_graph import DependencyGraph


def main():
    try:
        config = parse_arguments()
        print_config(config)

        # Построение графа
        graph = DependencyGraph(config.repo_url, config.test_mode)
        graph.build_graph(
            config.package_name,
            config.version if config.version else "latest",
            config.max_depth,
            config.filter_substring
        )

        # Вывод зависимостей
        print("\nПолученные зависимости:")
        print("------------------------------")
        for node, deps in graph.graph.items():
            print(f"{node}:")
            for dep in deps:
                print(f"  - {dep}")
        print("------------------------------")

        # Вывод порядка загрузки
        if config.load_order_mode:
            print("\nПорядок загрузки зависимостей (уровневый обход):")
            print("------------------------------")
            try:
                order = graph.get_load_order(config.package_name, config.version)
                for i, pkg in enumerate(order, 1):
                    print(f"{i:2d}. {pkg}")
            except Exception as e:
                print(f"Не удалось определить порядок загрузки: {e}")
            print("------------------------------")

        print("\nЭтап 4 завершён.\n")

    except Exception as e:
        print(f"Ошибка: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()