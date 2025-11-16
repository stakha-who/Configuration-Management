import sys
from config import parse_arguments, print_config
from dependency_loader import (
    load_repository_local,
    recursive_collect_http,
    recursive_collect_http
)


def main():
    try:
        config = parse_arguments()
        print_config(config)

        if config.test_mode:
            print("\nРабота в режиме test-mode")
            repo = load_repository_local(config.repo_url)
            print(repo)
        else:
            print("\nЗагрузка pom-файлов из Maven Central...")
            deps = recursive_collect_http(
                config.package_name,
                config.repo_url,
                config.version if config.version else "LATEST",
                config.max_depth,
            )

            print("\nПолученные зависимости:")
            print("------------------------------")

            for pkg, dlist in deps.items():
                if config.filter_substring:
                    dlist = [d for d in dlist if config.filter_substring in d]

                print(f"{pkg}:")
                for d in dlist:
                    print(f"  - {d}")

            print("------------------------------")

        print("\nЭтап 2 завершён.\n")

    except Exception as e:
        print(f"Ошибка: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
