# ParserWeb
Для корректной работы необходимо:
1. Скачать python3
2. Скачать PostgreSQL
3. Ввести в ParserWeb/settings.py в переменную DATABASES соответсвующие данные своей БД
4. Иметь интернет-подключение


Для запуска необходимо выполнить следующие шаги:
1. в терминале перейти в папку проекта
2. python prerun.py 
3. python manage.py makemigrations
4. python manage.py migrate
5. python manage.py runserver
