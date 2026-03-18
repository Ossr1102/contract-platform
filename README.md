# Contract Platform (FastAPI + Postgres + Redis)

This folder contains a self-contained contract management backend as described in the attached architecture plan (OTP auth, org scoping, contracts, licensing, billing, jobs).

## Quickstart (Docker)

1. From this folder, create a `.env` (optional) or rely on defaults.
2. Start services:

```bash
docker compose up --build
```

3. Apply migrations:

```bash
docker compose exec api alembic upgrade head
```

4. Open API docs at `http://localhost:8000/docs`.

## Local dev (no Docker)

```bash
python -m venv .venv
. .venv/Scripts/activate
pip install -r requirements.txt
set DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/contract_platform
set REDIS_URL=redis://localhost:6379/0
alembic upgrade head
uvicorn app.main:app --reload
```

