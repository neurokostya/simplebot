FROM python:3.11-slim

WORKDIR /app

# Устанавливаем зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем файлы проекта
COPY . .

# Настраиваем переменные окружения для Python
ENV PYTHONUNBUFFERED=1

# Запускаем бота
CMD ["python", "-u", "bot.py"] 