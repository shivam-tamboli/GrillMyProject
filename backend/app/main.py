from fastapi import FastAPI

from app.routes import auth, health, resume

app = FastAPI(title="GrillMyProject")

app.include_router(health.router)
app.include_router(auth.router)
app.include_router(resume.router)
