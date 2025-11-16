import sys
from config import parse_arguments, print_config
from maven_repository import MavenRepository
from test_repository import TestRepository
from dependency_graph import build_dependency_graph_recursive_bfs


def main():
    try:
        config = parse_arguments()
        print_config(config)

        if config.test_mode:
            repo = TestRepository(config.repo_url)
            print("\nРабота в режиме test-mode")
        else:
            repo = MavenRepository(config.repo_url)
            print("\nЗагрузка pom-файлов из Maven Central...")

        # Строим граф зависимостей рекурсивным BFS
        graph = build_dependency_graph_recursive_bfs(
            repo=repo,
            root_package=config.package_name,
            version=config.version if config.version else "latest",
            max_depth=config.max_depth,
            filter_substring=config.filter_substring
        )

        print("\nПолученные зависимости:")
        print("------------------------------")
        for node, deps in graph.items():
            print(f"{node}:")
            for dep in deps:
                print(f"  - {dep}")
        print("------------------------------")

        print("\nЭтап 3 завершён.\n")

    except Exception as e:
        print(f"Ошибка: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()