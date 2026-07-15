# Code review and improvement backlog

## Completed in this cleanup

1. Established one canonical `weather_outfit_adk` package instead of up to eight identical copies.
2. Removed generated workspace state, cached bytecode, pasted artifacts, packaged copies, and unused developer files.
3. Moved the web app, tests, deployment files, and documentation into clear top-level folders.
4. Removed an unused duplicate outfit-generation function from the Flask server.
5. Removed a second weather cache and routed web requests through the canonical cached weather tool.
6. Removed the hard-coded UV value, which presented invented data as real data.
7. Aligned the sample configuration, settings object, Docker Compose file, and Kubernetes manifest on `RAPIDAPI_KEY`, matching the implementation.
8. Made JSON request parsing tolerant of empty or malformed request bodies.
9. Split normal web dependencies from optional Google ADK dependencies.

## Highest-priority next improvements

### 1. Break up the Flask server

`app/server.py` is still too large and mixes routing, chat interpretation, preference handling, and response composition. Move routes into blueprints and move business logic into services.

Suggested target:

```text
app/
├── routes/
│   ├── weather.py
│   ├── outfit.py
│   └── chat.py
├── services/
│   ├── chat_service.py
│   └── weather_service.py
└── validation.py
```

### 2. Make weather failures explicit

The weather tool currently falls back to Seattle coordinates for an unknown city and returns demo weather after API failures. Return a structured `is_demo` or `data_status` field and show that state prominently in the interface. Unknown cities should return a validation error rather than silently becoming Seattle.

### 3. Replace the daily historical endpoint

The implementation calls a daily Meteostat endpoint for “current” conditions and derives several fields. Use a provider endpoint designed for current conditions and forecasts, then map provider responses into the existing schemas.

### 4. Validate all API inputs

Add limits and schemas for city names, chat messages, style arrays, activity values, and request sizes. Standardize error responses and status codes.

### 5. Secure production defaults

Restrict CORS to configured origins, add rate limiting, add security headers, disable detailed upstream errors in client responses, and add a production configuration object.

### 6. Modularize the browser code

`app/static/app.js` is a large class containing state, API calls, rendering, overlays, and recommendation shortcuts. Split it into modules for API access, state, rendering, preferences, and chat. Replace remaining HTML-template rendering with DOM construction where practical.

### 7. Remove duplicated recommendation concepts

There are two active recommendation systems: `app/outfit_generator.py` and `weather_outfit_adk/tools/outfit_tools.py`. Decide which is authoritative, expose it through one service, and test a single rule set.

### 8. Strengthen tests and automation

Add Flask endpoint tests, mocked provider tests, edge-case tests for temperature/rain/wind boundaries, JavaScript tests, formatting, linting, and a CI workflow.

### 9. Reassess the multi-agent layer

The web app currently has `USE_ADK_AGENTS = False`, so the optional multi-agent system is not used by the normal runtime. Decide whether it is a real product path. If yes, make it configurable and test it. If not, remove it to reduce maintenance and deployment complexity.
