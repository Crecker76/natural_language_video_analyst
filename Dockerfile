# Базовый образ Python
FROM python:3.11-slim

# Устанавливаем рабочую директорию в контейнере
WORKDIR /
# Копируем файл зависимостей в контейнер
COPY requirements.txt .

# Добавление PostgreSQL и зависимостей для сборки psycopg2
RUN apt-get update && apt-get install -y \
    libpq-dev gcc
# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt
# Устанавливаем клиент PostgreSQL
RUN apt-get update && apt-get install -y postgresql-client


# Указываем файл с переменными окружения
ENV PYTHONUNBUFFERED=1

# Определяем команду для запуска приложения
CMD ["python", ""]
