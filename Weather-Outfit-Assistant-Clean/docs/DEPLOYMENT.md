# Deployment

## Web application

Install the normal dependencies and start Gunicorn:

```bash
pip install -r requirements.txt
gunicorn --bind 0.0.0.0:${PORT:-5000} app:app
```

Set `RAPIDAPI_KEY` as a secret in the hosting platform. Do not commit `.env`.

## Optional A2A services

Install `requirements-adk.txt` for direct local development, or use Docker Compose:

```bash
cd deployment/a2a
docker compose up --build
```

The Docker build context is the repository root so every service imports the single canonical `weather_outfit_adk/` package.
