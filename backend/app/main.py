from fastapi import FastAPI

from app.routes import auth, health

app = FastAPI(title="GrillMyProject")

app.include_router(health.router)
app.include_router(auth.router)
