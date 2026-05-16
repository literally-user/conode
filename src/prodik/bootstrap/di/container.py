from dishka import AsyncContainer, make_async_container
from dishka.integrations.fastapi import FastapiProvider

from prodik.bootstrap.di.providers import (
    ApplicationProvider,
    CacheConnectionProvider,
    DatabaseConnectionProvider,
    InfrastructureProvider,
)
from prodik.infrastructure.config import (
    APIConfig,
    CacheConfig,
    Config,
    DatabaseConfig,
    SecretsConfig,
)


def get_async_container(config: Config) -> AsyncContainer:
    return make_async_container(
        FastapiProvider(),
        InfrastructureProvider(),
        ApplicationProvider(),
        CacheConnectionProvider(),
        DatabaseConnectionProvider(),
        context={
            APIConfig: config.api,
            DatabaseConfig: config.database,
            SecretsConfig: config.secrets,
            CacheConfig: config.cache,
        },
    )
