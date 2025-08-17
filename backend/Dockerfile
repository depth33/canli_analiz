FROM python:3.10-slim

# Sistem bağımlılıkları (isteğe bağlı, daha hızlı build için minimum tuttuk)
RUN pip install --no-cache-dir --upgrade pip

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Render/hosting ortamları genelde bir PORT env verir; yoksa 8000'e düşer
ENV PORT=8000

CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT}"]
