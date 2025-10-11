# Комплексное тестирование всех функций эмулятора

echo "1. ТЕСТ НАЧАЛЬНОГО СОСТОЯНИЯ И КОМАНДЫ WHO"
who
ls

echo "2. НАВИГАЦИЯ ПО КОРНЕВОЙ ДИРЕКТОРИИ"
ls /
cd /etc
ls
cd /var
ls
cd /home
ls

echo "3. МНОГОУРОВНЕВАЯ НАВИГАЦИЯ"
cd user/documents
ls
cd ../..
ls
cd /home/user/documents
ls

echo "4. ТЕСТИРОВАНИЕ КОМАНДЫ rev"
echo "Переворачиваем текст:"
rev Hello World
echo "Переворачиваем содержимое файла multi_line.txt:"
rev multi_line.txt
echo "Переворачиваем содержимое файла project1.txt:"
rev project1.txt

echo "5. ТЕСТИРОВАНИЕ КОМАНДЫ FIND"
echo "Поиск всех .txt файлов в /home:"
find /home -name *.txt
echo "Поиск файлов с 'project' в имени:"
find /home -name *project*
echo "Поиск файлов в текущей директории:"
find . -name *.txt

echo "6. ОБРАБОТКА ОШИБОК"
echo "Попытка перейти в несуществующую директорию:"
cd /nonexistent_directory
echo "Попытка осмотра несуществующего пути:"
ls /invalid_path
echo "Попытка найти в несуществующей директории:"
find /nonexistent -name *.txt
echo "Попытка перевернуть несуществующий файл:"
rev nonexistent_file.txt

echo "Скрипт завершен"