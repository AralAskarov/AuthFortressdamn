# Dockerfile
FROM python:3.10-slim

# Установка зависимостей
RUN apt-get update && apt-get install -y libpq-dev && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Копируем requirements и устанавливаем зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем проект
COPY . .

# Копируем скрипт ожидания базы данных
COPY wait-for-it.sh /wait-for-it.sh
RUN chmod +x /wait-for-it.sh

# Команда по умолчанию для запуска приложения
CMD ["/wait-for-it.sh", "db:5432", "--", "gunicorn", "tokendamn.wsgi:application", "--bind", "0.0.0.0:8000"]
