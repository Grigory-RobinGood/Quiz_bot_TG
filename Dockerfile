# Базовый образ с Python 3.12
FROM python:3.12-slim

# Устанавливаем системные зависимости для PostgreSQL и компиляции
RUN apt-get update && apt-get install -y \
    libpq-dev \
    python3-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Рабочая директория
WORKDIR /app

# Копируем зависимости
COPY requirements.txt .

# Устанавливаем Python-пакеты
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Копируем весь проект
COPY . .

# Для вебхуков нужно указать порт (по умолчанию для long polling не требуется)
# EXPOSE 80 443 8080

# Команда запуска (используем long polling по умолчанию)
CMD ["python", "bot.py"]