from collections.abc import AsyncIterator

from dishka import Provider, Scope, WithParents, provide, provide_all
from redis.asyncio import Redis
from sqlalchemy import URL
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from prodik.infrastructure.config import CacheConfig, DatabaseConfig
from prodik.infrastructure.transaction_manager import TransactionManagerImpl


class ConnectionProvider(Provider):
    provides = provide_all(WithParents[TransactionManagerImpl], scope=Scope.REQUEST)

    @provide(scope=Scope.APP)
    async def provide_async_engine(
        self, config: DatabaseConfig
    ) -> AsyncIterator[async_sessionmaker[AsyncSession]]:
        engine = create_async_engine(
            url=URL.create(
                "postgresql+asyncpg",
                username=config.username,
                password=config.password,
                database=config.database,
                port=config.port,
                host=config.host,
            ),
            pool_size=5,
            max_overflow=96,
            pool_timeout=30,
        )
        yield async_sessionmaker(
            engine,
            expire_on_commit=False,
        )
        await engine.dispose()

    @provide(scope=Scope.REQUEST)
    async def provide_async_session(
        self,
        session_factory: async_sessionmaker[AsyncSession],
    ) -> AsyncIterator[AsyncSession]:
        async with session_factory() as session:
            yield session

    @provide(scope=Scope.REQUEST)
    async def provide_redis_connection(
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
