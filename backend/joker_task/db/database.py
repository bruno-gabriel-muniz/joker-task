from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from joker_task.settings import Settings

engine = create_async_engine(Settings().DATABASE_URL)  # type: ignore


async def get_session():
    logger.info('starting a session in the database')  # pragma: no cover
    async with AsyncSession(
        engine,
    ) as session:  # pragma: no cover
        yield session
