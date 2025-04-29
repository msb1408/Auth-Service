FROM python:3.9-slim

WORKDIR /app

# Установка Poetry
RUN pip install poetry

# Копирование файлов проекта
COPY pyproject.toml ./

# Установка зависимостей
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --no-root

# Копирование исходного кода
COPY . .

# Запуск приложения
CMD ["poetry", "run", "uvicorn", "auth_server:app", "--host", "0.0.0.0", "--port", "8000"] 