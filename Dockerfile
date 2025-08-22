FROM python:3.10-slim

WORKDIR /app

# Копируем requirements.txt и устанавливаем зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь код
COPY . .

# Запускаем сервер
CMD ["uvicorn", "app:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]