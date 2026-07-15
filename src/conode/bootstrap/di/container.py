from dishka import AsyncContainer, make_async_container
from dishka.integrations.fastapi import FastapiProvider

from conode.bootstrap.di.providers import (
    ApplicationProvider,
    ConnectionProvider,
    InfrastructureProvider,
    SecretsProvider,
)
from conode.infrastructure.config import (
    APIConfig,
    Config,
    DatabaseConfig,
    SecretsConfig,
)


def get_async_container(config: Config) -> AsyncContainer:
    return make_async_container(
        FastapiProvider(),
        InfrastructureProvider(),
        ApplicationProvider(),
        SecretsProvider(),
        ConnectionProvider(),
        context={
            APIConfig: config.api,
            DatabaseConfig: config.database,
            SecretsConfig: config.secrets,
        },
    )
