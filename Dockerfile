# Используем официальный образ Python
FROM python:3.11-slim

# Устанавливаем метаданные
LABEL maintainer="EduVerse Team <support@eduverse.com>"
LABEL version="1.0.0"
LABEL description="EduVerse - Образовательная платформа нового поколения"

# Устанавливаем рабочую директорию
WORKDIR /app

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Копируем файлы зависимостей
COPY requirements.txt .

# Устанавливаем Python зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем исходный код приложения
COPY . .

# Создаем необходимые директории
RUN mkdir -p uploads logs backups instance

# Создаем пользователя для безопасности
RUN useradd --create-home --shell /bin/bash eduverse \
    && chown -R eduverse:eduverse /app

# Переключаемся на пользователя eduverse
USER eduverse

# Открываем порт
EXPOSE 5000

# Устанавливаем переменные окружения по умолчанию
ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV PYTHONPATH=/app

# Проверка здоровья приложения
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Команда запуска
CMD ["python", "run.py"]