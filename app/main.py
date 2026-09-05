from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import engine, Base
from .migrations import run_migrations
from .models import models  # noqa: F401 — trigger table registration
from .routers import admin, auth, exercise_progress, progress, test_results

Base.metadata.create_all(bind=engine)
run_migrations(engine)

app = FastAPI(
    title="Sog'lom Pedagog API",
    description="OTM pedagoglari uchun WFSIP jismoniy faollik ilovasi — backend",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # prod da Flutter app URL ga o'zgartiring
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(progress.router)
app.include_router(exercise_progress.router)
app.include_router(test_results.router)


@app.get("/")
def root():
    return {"status": "ok", "service": "Sog'lom Pedagog API v1.0"}


@app.get("/health")
def health():
    return {"status": "healthy"}
