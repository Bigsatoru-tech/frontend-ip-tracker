# Visitor Tracker backend (V1)

FastAPI + SQLAlchemy + SQLite. Records time, device and approximate location for each page visit.

## Folder structure

```
backend/
  core/        config.py (settings), database.py (engine/session), security.py (admin key check),
               tracker.py (User-Agent parsing + IP location lookup)
  models/      database tables (visit.py)
  schemas/     request/response shapes (visit.py)
  crud/        database operations (visit.py)
  routers/     API endpoints (visits.py)
  tests/       pytest tests
  seed.py      demo data
  main.py      creates the app and wires everything together
```

## Run it

Run every command from the folder that **contains** `backend/` (the project root).

```bash
python -m venv .venv
.venv\Scripts\activate                 # Windows   (Linux/Mac: source .venv/bin/activate)
pip install -r backend/requirements.txt
copy backend\.env.example backend\.env # Linux/Mac: cp backend/.env.example backend/.env, then edit it
uvicorn backend.main:app --reload
```

Docs and a try-it page: http://127.0.0.1:8000/docs

## Location lookup (optional, needed for real locations)

1. Create a free MaxMind account and download **GeoLite2 City** (`GeoLite2-City.mmdb`).
2. Put it in the `backend/` folder (or set `GEOIP_DB_PATH` in `.env`).

Without the file everything still works; location shows "Unknown".

## Endpoints

| Method | Path | Purpose |
| --- | --- | --- |
| POST | `/api/visit` | Frontend calls this once on page load. Saves the visit and returns the card details. |
| GET | `/api/visits?limit=50` | Newest first, max 100. Needs header `X-API-Key: <ADMIN_KEY>`. |
| GET | `/health` | Liveness check. |

`POST /api/visit` body: `{"page_path": "/"}`. Response:

```json
{"ip_address": "102.89.0.0", "location": "Port Harcourt, Rivers, Nigeria",
 "browser": "Chrome", "os": "Android", "device": "Mobile",
 "visited_at": "2026-11-01T12:00:00Z"}
```

## Frontend hookup

On page load, call `POST {BACKEND_URL}/api/visit` and render the response in the "This is you" card.
Add the frontend's origin to `CORS_ORIGINS` in `.env`.

## Testing with fake visitors

With `APP_ENV=dev`, send `X-Debug-IP: <public ip>` to pretend to be another visitor (ignored in prod):

```bash
curl -X POST localhost:8000/api/visit -H "Content-Type: application/json" -H "X-Debug-IP: 102.89.45.7" -d "{\"page_path\":\"/\"}"
```

## Demo data

```bash
python -m backend.seed            # 30 sample visits
python -m backend.seed --clear    # delete ALL rows
```

## Tests

```bash
pytest backend/tests
```

(Creates `test_visits.db` in the folder you run it from; delete it afterwards.)

## Deploying

Set `APP_ENV=prod`, `TRUST_PROXY=true` (only if your host sets `X-Forwarded-For`), a real `ADMIN_KEY`,
and `CORS_ORIGINS` to your frontend URL. Then check that the stored IP is the visitor's, not the proxy's.

## Privacy

Only a truncated IP (`102.89.0.0`) is stored. Location is looked up from the full IP before truncating.
Query strings are stripped from page paths. Add a privacy note before using on real public traffic.
