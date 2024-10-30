import logging
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from database_model.tables import Base
from database_model.triggers import (
    setup_user_accounts_triggers,
    setup_user_mails_triggers,
    setup_user_names_triggers,
    setup_user_avatars_triggers
)
from settings import settings




engine = create_async_engine(settings.database_url)
async_session_local = async_sessionmaker(bind=engine, expire_on_commit=False)


async def create_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await conn.run_sync(Base.metadata.create_all)
        await setup_user_accounts_triggers(engine)
        await setup_user_mails_triggers(engine)
        await setup_user_names_triggers(engine)
        await setup_user_avatars_triggers(engine)


async def get_db() -> AsyncSession:
    async with async_session_local() as session:
        yield session

