# Weather Outfit Assistant

A Flask web application that combines weather data with activity, comfort, and style preferences to recommend practical outfits. The default web experience uses deterministic recommendation logic and can run without an AI model key. An optional Google ADK multi-agent deployment remains available under `deployment/a2a/`.

## Project structure

```text
.
├── app/                         # Flask web application, templates, and browser code
├── weather_outfit_adk/          # Canonical agents, tools, schemas, memory, and monitoring
├── deployment/a2a/              # Optional multi-service ADK deployment
├── docs/                        # Architecture, review, and maintenance notes
├── tests/                       # Lightweight tests plus optional ADK checks
├── .env.example
├── requirements.txt             # Web application dependencies
├── requirements-adk.txt         # Optional multi-agent dependencies
└── run.py                       # Local entry point
```

## Run locally

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS or Linux
source .venv/bin/activate

pip install -r requirements.txt
copy .env.example .env           # Windows
# cp .env.example .env           # macOS/Linux
python run.py
```

Open `http://localhost:5000`. Without `RAPIDAPI_KEY`, the weather tool returns clearly labeled demo data.

## Run tests

```bash
python -m unittest tests.test_tools
```

The optional agent tests require:

```bash
pip install -r requirements-adk.txt
python tests/test_adk_imports.py
```

## Production

A simple Gunicorn command is:

```bash
gunicorn --bind 0.0.0.0:$PORT app:app
```

See `docs/CODE_REVIEW.md` for the prioritized improvement backlog and `docs/ARCHITECTURE.md` for the cleanup decisions.
