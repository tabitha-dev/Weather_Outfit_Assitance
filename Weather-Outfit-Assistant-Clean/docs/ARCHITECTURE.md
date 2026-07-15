# Architecture and cleanup decisions

## Canonical source

`weather_outfit_adk/` is the only copy of the Python domain package. The web application and every optional deployment service import this shared package. Deployment folders no longer vendor complete copies of the source tree.

## Web application

`app/server.py` owns HTTP routes. `app/outfit_generator.py` owns the larger presentation-oriented outfit generator. Browser assets live beside the Flask templates under `app/static/` and `app/templates/`.

## Removed generated and archival material

The cleaned project intentionally excludes workspace metadata, local editor state, Git internals, Python bytecode, pasted development artifacts, old packaged exports, an unused status server, a developer icon page, and an unreferenced legacy stylesheet. These files were not required to run or deploy the application.

## Dependency boundaries

The web app installs from `requirements.txt`. Google ADK and Uvicorn are isolated in `requirements-adk.txt` so the normal local application does not carry optional multi-agent dependencies.
