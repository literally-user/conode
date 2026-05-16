from collections.abc import AsyncIterator

from dishka import Provider, Scope, provide
from redis.asyncio import Redis

from prodik.infrastructure.config import CacheConfig


class CacheConnectionProvider(Provider):
    @provide(scope=Scope.APP)
    async def get_redis_connection(self, config: CacheConfig) -> AsyncIterator[Redis]:
        client = Redis(
            host=config.host,
            port=config.port,
            decode_responses=True,
        )

        yield client

        await client.aclose()
