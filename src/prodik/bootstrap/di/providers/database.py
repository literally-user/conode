from collections.abc import AsyncIterator

from dishka import Provider, Scope, provide
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from prodik.infrastructure.config import CacheConfig, DatabaseConfig


class DatabaseConnectionProvider(Provider):
    @provide(scope=Scope.APP)
    async def get_engine(self, config: DatabaseConfig) -> AsyncIterator[AsyncEngine]:
        engine = create_async_engine(config.url, future=True)
        yield engine
        await engine.dispose()

    @provide(scope=Scope.APP)
    async def get_async_sessionmaker(
        self,
        engine: AsyncEngine,
    ) -> async_sessionmaker[AsyncSession]:
        return async_sessionmaker(
            engine,
            expire_on_commit=False,
        )

    @provide(scope=Scope.REQUEST)
    async def get_async_session(
        self,
        session_factory: async_sessionmaker[AsyncSession],
    ) -> AsyncIterator[AsyncSession]:
        async with session_factory() as session:
            yield session

    @provide(scope=Scope.REQUEST)
    async def get_redis_connection(
        self,
        config: CacheConfig,
    ) -> AsyncIterator[Redis]:
        client = Redis(
            host=config.host,
            port=config.port,
            decode_responses=True,
        )
        yield client
        await client.aclose()
