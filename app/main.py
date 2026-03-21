from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from app.config import PROJECT_ROOT, settings
from app.routers.web import router as web_router
from app.seed import initialize_database


@asynccontextmanager
async def lifespan(_app: FastAPI):
    initialize_database(with_demo_data=True)
    yield


app = FastAPI(
    title=settings.project_name,
    lifespan=lifespan,
)

app.add_middleware(SessionMiddleware, secret_key=settings.secret_key)
app.mount("/static", StaticFiles(directory=str(PROJECT_ROOT / "app" / "static")), name="static")
app.include_router(web_router)

