FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt requirements-adk.txt ./
RUN pip install --no-cache-dir -r requirements-adk.txt

COPY . .

ENV PYTHONPATH=/app
EXPOSE 8000

# Docker Compose overrides this command for each service.
CMD ["python", "deployment/a2a/coach_service/app.py"]
