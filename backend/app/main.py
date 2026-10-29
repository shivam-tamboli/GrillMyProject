from fastapi import FastAPI

from app.routes import health

app = FastAPI(title="GrillMyProject")

app.include_router(health.router)
