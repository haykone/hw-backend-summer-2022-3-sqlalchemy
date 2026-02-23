from typing import TYPE_CHECKING, Any

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.engine.url import URL
from app.store.database.sqlalchemy_base import BaseModel

if TYPE_CHECKING:
    from app.web.app import Application


class Database:
    def __init__(self, app: "Application") -> None:
        self.app = app
        self.engine: AsyncEngine | None = None
        self._db: type = BaseModel
        self.session: async_sessionmaker[AsyncSession] | None = None

    async def connect(self, *args: Any, **kwargs: Any) -> None:
        db_config = self.app.config.database

        self.engine = create_async_engine(
            URL.create(
                drivername="postgresql+asyncpg",
                host=db_config.host,
                database=db_config.database,
                username=db_config.user,
                password=db_config.password,
                port=db_config.port,
            ),
            echo=True,
        )

        self.session = async_sessionmaker(
            self.engine,
            expire_on_commit=False,
            class_=AsyncSession
        )

    async def disconnect(self, *args: Any, **kwargs: Any) -> None:
        if self.engine:
            await self.engine.dispose()
