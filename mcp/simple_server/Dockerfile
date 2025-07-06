FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml .
COPY server.py .

RUN pip install --no-cache-dir .

EXPOSE 8080

CMD ["python", "server.py"]