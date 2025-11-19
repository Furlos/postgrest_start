#!/bin/bash

# Запускаем PostgreSQL в фоне
service postgresql start

# Ждем запуска PostgreSQL
sleep 5

# Создаем пользователя и базу данных
su - postgres -c "psql -c \"CREATE USER test_user WITH PASSWORD 'test_password';\""
su - postgres -c "psql -c \"CREATE DATABASE test_db WITH OWNER test_user;\""
su - postgres -c "psql -c \"GRANT ALL PRIVILEGES ON DATABASE test_db TO test_user;\""

# Запускаем тесты
python -m pytest test_concurrency.py -v