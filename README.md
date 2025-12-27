Необходимые программы Docker Desktop, Python 3.11 или новее.

В папке проекта выполнить:
docker compose up -d db

После завершения, нужно проверить что база работает : 
docker compose ps

Установка зависимостей :
cd app

# Установка необходимых библиотек
pip install -r requirements.txt

# Запуск приложения
python main.py

После запуска приложения заполнить поля для подключения к базе данных :

Хост host.docker.internal
Порт 5432
База данных clothingstoredb
Пользователь postgres
Пароль 12345