# Backend

FastAPI + PostgreSQL (SQLAlchemy).

## Run

```
cd backend
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # set DATABASE_URL
uvicorn app.main:app --reload
```

Check it works: `GET http://localhost:8000/health`

## Structure

- `app/routes` - API endpoints
- `app/models` - SQLAlchemy models (tables)
- `app/schemas` - request/response shapes
- `app/services` - business logic
- `app/core` - config
- `app/db` - engine, session, Base
