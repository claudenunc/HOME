# Weaver Protocol — Hosted API

FastAPI service wrapping `weaver-protocol` for the hosted paid tier.

## Quickstart (local)

```bash
cd api/
pip install -r requirements.txt
WEAVER_API_KEYS="your-key-here" uvicorn main:app --reload
```

Without `DATABASE_URL` the API runs with an in-memory session store — all data
is lost on restart. For persistence, add Postgres (see below).

Docs at `http://localhost:8000/docs`.

## Endpoints

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/health` | None | Health check |
| POST | `/verify` | Bearer | Run multi-observer verification |
| GET | `/session/{id}` | Bearer | Retrieve session provenance |
| GET | `/drift-log/summary` | Bearer | Drift log aggregate stats |

## Authentication

Set `WEAVER_API_KEYS` env var to a comma-separated list of valid bearer tokens:

```
WEAVER_API_KEYS="sk-abc123,sk-def456"
```

Clients pass the token as `Authorization: Bearer <key>`.

## Postgres (persistent session store)

Set `DATABASE_URL` and the API auto-creates the schema on first boot:

```
DATABASE_URL=postgres://user:pass@host:5432/weaver
```

Without it, sessions live in memory only (fine for dev; not production).

## Deploy to Railway

1. `railway init` in this directory
2. Provision a Postgres plugin — Railway sets `DATABASE_URL` automatically
3. Set `WEAVER_API_KEYS` in Railway environment variables
4. Set `ANTHROPIC_API_KEY` / `OPENAI_API_KEY` as needed for live adapters
5. `railway up`

## Deploy to Render

1. New Web Service → connect repo → set root to `LIVE/weaver-protocol/api/`
2. Build: `pip install -r requirements.txt`
3. Start: `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. Add a Render Postgres instance → copy the Internal Database URL → set as `DATABASE_URL`
5. Set env vars: `WEAVER_API_KEYS`, `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`

## Docker

```bash
docker build -t weaver-api .
docker run -e WEAVER_API_KEYS="sk-abc123" -p 8000:8000 weaver-api
```

## Pricing (live tier)

| Plan | Monthly | Included verifications |
|---|---|---|
| Starter | $49/mo | 500 verifications |
| Pro | $199/mo | 5,000 verifications |
| Enterprise | $499+/mo | Unlimited + SLA |

Contact: aetherkin.ai/intake
