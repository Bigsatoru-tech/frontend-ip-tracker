from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import models  # noqa: F401  (importing it registers the tables)
from core.config import get_settings
from core.database import Base, engine
from routers import visits

settings = get_settings()

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Visitor Tracker")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

app.include_router(visits.router)


@app.get("/health")
def health():
    return {"status": "ok"}
