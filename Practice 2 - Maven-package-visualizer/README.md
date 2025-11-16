# Maven Package Visualizer

*Инструмент для визуализации графа зависимостей пакетов Maven, а также тестовых пакетов.*

## Функциональность
- конфигурация через параметры командной строки;
- валидация входных параметров;
- вывод настроек в формате ключ-значение.

## Использование

Общий вид команды для запуска:

```bash
python src/cli.py --package <имя_пакета> --repo <url_репозитория> [опции]
```

**Допускается использование сокращений для параметров, они указаны в таблице «Доступные параметры»**

Продемонстрируем работу приложения на примере Maven-репозитория (https://repo.maven.apache.org/maven2).

Структура этого репозитория:
https://repo.maven.apache.org/maven2/GROUP_ID/ARTIFACT_ID/VERSION/

Рассмотрим на примере для **commons-lang3 версии 3.0**:
- GROUP_ID: `org.apache.commons`.
- ARTIFACT_ID: `commons-lang3`.
- VERSION: `3.0`.

Таким образом, запуск будет осуществлен со следующими параметрами:
```bash
python cli.py --package org.apache.commons:commons-lang3 --repo https://repo.maven.apache.org/maven2/ -v 3.0
```

## Доступные параметры
 Параметр | Описание | Пример ввода
|:----------:|:----------:|:----------:
| `--package / -p` `<имя_пакета>`    | `Имя анализируемого пакета (обязательный)`  | `-p org.apache.commons:commons-lang3` |
| `--repo / -r` `<ссылка_на_репозиторий>`    | `URL репозитория или путь к файлу тестового репозитория (обязательный)`   | `-r https://repo.maven.apache.org/maven2/` |
| `--test-mode / -t`   | `Режим работы с тестовым репозиторием` | `-t` |
| `--version / -v` `<номер_версии>` | `Версия пакета` | `-v 0.1.0` |
| `--ascii-tree / -a` | `Вывод графа зависимостей в форме ASCII-дерева` | `-a` |
| `--graph / -g` | `Визуализация графа` | `-g` |
| `--output / -o` `<название_файла>` | `Имя сгенерированного файла с изображением графа` | `-o new_graph` |
| `--max-depth / -d` `<количество_уровней>` | `Максимальная глубина анализа зависимостей` | `-d 2` |
| `--filter / -f` `<подстрока>` | `Исключить пакеты, содержащие введенную подстроку` | `-f kotlin` |

## Примеры запуска

### Базовый запуск
```bash
python src/cli.py -p com.example:my-package -r https://repo.maven.apache.org/maven2/
```

### С тестовым режимом
```bash
python src/cli.py -p TEST_PACKAGE -r tests/test_repo.txt -t
```
**Примечание: для корректной работы программы при использовании тестовых репозиториев необходим тестовый режим (`--test-mode / -t`).**

### С дополнительными параметрами
```bash
python src/cli.py -p com.example:lib -r /path/to/repo -v 1.0.0 -o graph.svg -d 3
```

## Тестирование

**Тест 1: запуск с корректными параметрами**
```bash
python cli.py --package org.apache.commons:commons-lang3 --repo https://repo.maven.apache.org/maven2/ -v 3.0
```

**Вывод**
```bash
Текущая конфигурация:
------------------------------
package_name: org.apache.commons:commons-lang3
repo_url: https://repo.maven.apache.org/maven2/
test_mode: False
version: 3.0
output_file: dependency_graph.png
ascii_mode: False
max_depth: unlimited
filter_substring: none
------------------------------

Этап 1 завершён: параметры успешно получены и провалидированы.
```
\
**Тест 2: обработка ошибок**
```bash
python cli.py --package "" --repo https://repo.maven.apache.org/maven2/
```

**Вывод**
```bash
Ошибка: Имя пакета обязательно для указания
```