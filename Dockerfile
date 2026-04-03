FROM python:3.12-alpine

RUN pip install --upgrade pip

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PORT=8080
EXPOSE 8080

RUN adduser -D -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 app:app
