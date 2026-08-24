import os
from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel import SQLModel, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models import Course, User

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "sqlite+aiosqlite:///school.sqlite",
)

engine = create_async_engine(DATABASE_URL)


async def get_session() -> AsyncIterator[AsyncSession]:
    async with AsyncSession(engine, expire_on_commit=False) as session:
        yield session


async def prepare_database() -> None:
    async with engine.begin() as connection:
        await connection.run_sync(SQLModel.metadata.create_all)

    async with AsyncSession(engine) as session:
        if (await session.exec(select(Course))).first() is not None:
            return

        session.add_all(
            [
                Course(
                    title="JavaScript",
                    description="Курс по языку программирования JavaScript",
                ),
                Course(
                    title="FastAPI", description="Курс по фреймворку FastAPI"
                ),
                User(name="admin", email="admin@example.com", password="admin"),
            ]
        )
        await session.commit()
