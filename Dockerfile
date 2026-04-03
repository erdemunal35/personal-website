FROM python:3.12-slim

# Upgrade pip to address CVE-2025-8869 and CVE-2026-1703
RUN pip install --upgrade "pip>=25.3"

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PORT=8080
EXPOSE 8080

RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 app:app
