from fastapi import FastAPI

from app.routes import auth, health, interview, resume, session

app = FastAPI(title="GrillMyProject")

app.include_router(health.router)
app.include_router(auth.router)
app.include_router(resume.router)
app.include_router(session.router)
app.include_router(interview.router)
