# Комплексное тестирование всех команд эмулятора

echo "1. ТЕСТИРОВАНИЕ КОМАНДЫ who"
who

echo "2. ТЕСТИРОВАНИЕ КОМАНДЫ echo"
echo "Простой текст"
echo "Текст с переменными: Пользователь $USER, домашняя директория $HOME"
echo "Множественные аргументы: арг1 арг2 арг3"

echo "3. ТЕСТ НАЧАЛЬНОГО СОСТОЯНИЯ И КОМАНДЫ ls"
echo "Текущая директория:"
ls
echo "Корневая директория:"
ls /
echo "Директория /home:"
ls /home

echo "4. ТЕСТИРОВАНИЕ КОМАНДЫ cd"
echo "Переход в /etc:"
cd /etc
ls
echo "Возврат в домашнюю директорию:"
cd /home/user
ls
echo "Относительные пути - переход в documents:"
cd documents
ls
echo "Возврат на уровень выше:"
cd ..
ls
echo "Переход в корень и обратно:"
cd /
ls
cd /home/user

echo "5. ТЕСТИРОВАНИЕ КОМАНДЫ mkdir"
echo "Создание новой директории 'test_dir':"
mkdir test_dir
ls
echo "Создание вложенной директории 'test_dir/subdir':"
mkdir test_dir/subdir
ls test_dir
echo "Попытка создать существующую директорию:"
mkdir test_dir
echo "Попытка создать директорию с именем существующего файла:"
mkdir multi_line.txt

echo "6. ТЕСТИРОВАНИЕ КОМАНДЫ rev"
echo "Переворачивание текста:"
rev Hello World
echo "Переворачивание русского текста:"
rev Привет Мир
echo "Переворачивание содержимого файла multi_line.txt:"
rev multi_line.txt
echo "Переворачивание содержимого файла project1.txt:"
rev project1.txt

echo "7. ТЕСТИРОВАНИЕ КОМАНДЫ find"
echo "Поиск всех .txt файлов в /home:"
find /home -name*.txt
echo "Поиск файлов с 'project' в имени:"
find /home -name *project*
echo "Поиск файлов в текущей директории:"
find . -name *.txt
echo "Поиск всех файлов в /etc:"
find /etc -name *

echo "8. ТЕСТИРОВАНИЕ ВМЕСТЕ НОВЫХ ДИРЕКТОРИЙ"
echo "Переход в созданную директорию:"
cd test_dir
ls
echo "Создание дополнительной директории:"
mkdir another_dir
ls
echo "Поиск в новой структуре:"
find . -name *

echo "9. ОБРАБОТКА ОШИБОК"
echo "Попытка перейти в несуществующую директорию:"
cd /nonexistent_directory
echo "Попытка осмотра несуществующего пути:"
ls /invalid_path
echo "Попытка найти в несуществующей директории:"
find /nonexistent -name *.txt
echo "Попытка перевернуть несуществующий файл:"
rev nonexistent_file.txt
echo "Попытка создать директорию с неверным путем:"
mkdir /invalid/path/test

echo "Скрипт завершен"