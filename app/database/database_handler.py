from settings import settings
from model.tables import Base
from sqlalchemy.ext.asyncio import (
    create_async_engine, 
    async_sessionmaker,
)

class DatabaseManager:
    def __init__(self):
        self._engine = create_async_engine(settings.DATABASE_URL)
        self._async_session_local = async_sessionmaker(bind=self._engine, 
                                                       expire_on_commit=False)
    async def create_db(self):
        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def get_db(self):
        async with self._async_session_local() as session:
            yield session

