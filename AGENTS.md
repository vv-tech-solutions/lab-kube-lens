# AGENTS.md

This file contains concise instructions for OpenCode agents and new developers to work in this repository without guesswork.

## Quick start

- **Install dependencies** (editable mode + dev tools):
  ```bash
  pip install -e ".[dev]"
  ```

- **Set up environment variables** – create a `.env` file with the following keys (copy from `.env.example` if present):
  ```dotenv
  OLLAMA_URL=http://localhost:11434/api
  QDRANT_HOST=localhost
  QDRANT_PORT=6333
  ```
  These values are used by `app.settings.Settings`.

- **Run the API locally**:
  ```bash
  export PYTHONPATH=$PYTHONPATH:$(pwd)/src  # only if you didn't use editable install
  uvicorn app.server:app --reload
  ```
  The server exposes:
  - `GET /health` – health‑check (returns `{\"status\":\"OK\"}`)
  - `POST /analyze` – streaming NDJSON analysis of the provided log content. The request body must be JSON with a single field `content` (≤1500 chars).

- **Alternatively** start the full stack with Docker Compose:
  ```bash
  docker compose up
  ```
  This brings up the API and a Qdrant instance. The API will automatically use `QDRANT_HOST=qdrant` when running in the compose network.

## Building a production image

The GitLab CI pipeline builds an ARM64 OCI image with `buildah`. Replicate locally with:
```bash
buildah build \
  --arch arm64 \
  -t oci.vvtechsolutions.eu/kube-lens:latest \
  --layers \
  .
```
To push to the registry you need credentials:
```bash
echo "$REGISTRY_PASSWORD" | buildah login -u "$REGISTRY_USER" --password-stdin oci.vvtechsolutions.eu
buildah push oci.vvtechsolutions.eu/kube-lens:latest
```
The CI job also tags with the short commit SHA – you can do the same with:
```bash
buildah tag oci.vvtechsolutions.eu/kube-lens:latest oci.vvtechsolutions.eu/kube-lens:${CI_COMMIT_SHORT_SHA}
buildah push oci.vvtechsolutions.eu/kube-lens:${CI_COMMIT_SHORT_SHA}
```

## Seeding Qdrant

After Qdrant is running (e.g. via Docker Compose), populate it with the bundled knowledge base:
```bash
python scripts/seed.py
```
This reads `data/knowledge_base.json`, creates the `sre_knowledge` collection (size = 768 Cosine), embeds each procedure with the Ollama embed model, and upserts the vectors.

## Important runtime details

- **Python version** – the project requires ≥ 3.11.
- **Qdrant** – the client defaults to `localhost:6333`. When using Compose, the host resolves to the service name `qdrant`.
- **Ollama** – the embed endpoint is `${OLLAMA_URL}/embed`; the chat endpoint is `${OLLAMA_URL}/chat`.
- **Streaming response** – `/analyze` returns `application/x-ndjson`. Consume the stream line‑by‑line; each line is a JSON object.
- **Logging** – the API prints system and user prompts to stdout for debugging.
- **Async** – all external calls (`httpx`) are asynchronous, and settings are injected per request via FastAPI `Depends`.

## Testing

The repository includes a `tests/` directory with unit tests. Run them with:
```bash
pytest --cov=src --cov-report=xml
```
Linting and type‑checking can be run manually with:
```bash
ruff check src/
ruff format --check src/
mypy src/
```

## Tooling

- **pyproject.toml** pins all runtime and dev dependencies (ruff, mypy, deptry, pytest, httpx, etc.).
- **CI** (GitLab) runs lint, type‑check, tests, security scan, and builds the Docker image.
- **Dependency injection** – use `from app.dependencies import get_settings` to inject settings into FastAPI routes.

> **Note**: All commands are intended to be run from the repository root.
