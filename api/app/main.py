from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.routers import elections, health, parties, polls, pollsters, results, timeseries


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title="Spain Electoral Polls API",
        description="Read-only API for Spain Electoral Polls data.",
        version="0.1.0",
    )

    origins = settings.cors_origin_list
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins or ["*"],
        allow_credentials=True,
        allow_methods=["GET"],
        allow_headers=["*"],
    )

    app.include_router(health.router)
    app.include_router(elections.router)
    app.include_router(pollsters.router)
    app.include_router(parties.router)
    app.include_router(polls.router)
    app.include_router(results.router)
    app.include_router(timeseries.router)
    return app


app = create_app()
