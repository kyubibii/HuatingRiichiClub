# Backend Quick Start

FastAPI backend for HuatingRiichiClub.

## Prerequisites

- Python 3.13+
- `uv`
- MySQL and Redis available locally or via Docker

## Install Dependencies

```bash
cd service/backend
uv sync
```

## Start Development Server

```bash
cd service/backend
uv run fastapi dev app/main.py
```

Or run uvicorn directly:

```bash
cd service/backend
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

After startup:

- API health: <http://localhost:8000/health>
- Swagger UI: <http://localhost:8000/docs>

## Environment

Copy the example env file and adjust values as needed:

```bash
cd service/backend
cp .env.example .env
```

Typical local dependencies:

- MySQL: `localhost:3306`
- Redis: `localhost:6379`

## Database Migration

```bash
cd service/backend
uv run alembic upgrade head
```

Create a new migration:

```bash
cd service/backend
uv run alembic revision --autogenerate -m "describe change"
```

## With Docker Dependencies

If MySQL and Redis are started from `service/docker-compose.yml`, the backend can still be run locally with `uv` while using those containers as dependencies.
