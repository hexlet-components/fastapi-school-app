from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from app.database import prepare_database
from app.routers import courses, root, users


@asynccontextmanager
async def lifespan(_app: FastAPI):
    # Таблицы и начальные данные создаются на старте: приложение учебное и
    # историю схемы не ведёт.
    await prepare_database()
    yield


app = FastAPI(lifespan=lifespan)
app.add_middleware(
    SessionMiddleware,
    secret_key="development-secret-change-me",
    session_cookie="school_session",
)

# Собранный css лежит в app/static: его пишет tailwind из assets/css/source.css.
app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(root.router)
app.include_router(courses.router)
app.include_router(users.router)
