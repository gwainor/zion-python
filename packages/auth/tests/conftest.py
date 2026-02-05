import os
from collections.abc import AsyncGenerator

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

os.environ["ZION_SETTINGS_MODULE"] = "tests.settings"


from zion.db import DbBaseModel


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture(scope="session")
def async_engine():
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
        future=True,
    )
    return engine


@pytest.fixture(scope="session")
async def setup_database(async_engine):
    async with async_engine.begin() as conn:
        await conn.run_sync(DbBaseModel.metadata.create_all)
    yield
    async with async_engine.begin() as conn:
        await conn.run_sync(DbBaseModel.metadata.drop_all)


@pytest.fixture
async def db_session(
    async_engine, setup_database
) -> AsyncGenerator[AsyncSession, None]:
    async_session = async_sessionmaker(
        bind=async_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    async with async_session() as session:
        yield session
        await session.rollback()
