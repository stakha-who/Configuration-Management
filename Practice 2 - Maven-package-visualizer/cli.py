import sys
from config import parse_arguments, print_config


def main():
    try:
        config = parse_arguments()
        print_config(config)

        print("\nЭтап 1 завершён: параметры успешно получены и провалидированы.\n")

    except Exception as e:
        print(f"Ошибка: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
