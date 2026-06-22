from collections.abc import AsyncIterator

import pytest
from dishka import AsyncContainer, Provider, Scope, make_async_container, provide
from dishka.integrations.fastapi import FastapiProvider, setup_dishka
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from prodik.application.interfaces.repositories import (
    LocalAuthorizationRepository,
    SessionRepository,
    UserRepository,
)
from prodik.application.interfaces.token_managers import (
    AccessTokenManager,
    RefreshTokenManager,
)
from prodik.application.interfaces.transaction_manager import TransactionManager
from prodik.bootstrap.api.run import create_app
from prodik.bootstrap.di.providers import (
    ApplicationProvider,
    CacheConnectionProvider,
    InfrastructureProvider,
)
from prodik.infrastructure.config import (
    APIConfig,
    CacheConfig,
    Config,
    DatabaseConfig,
    SecretsConfig,
    load_config,
)
from prodik.infrastructure.persistence import start_mapper
from tests.factories.models import UserFactory


@pytest.fixture(scope="session")
def config() -> Config:
    return load_config("test.config.toml")


@pytest.fixture(scope="session", autouse=True)
def startup() -> None:
    start_mapper()


@pytest.fixture
async def user_factory(container: AsyncContainer) -> UserFactory:
    async with container() as test_container:
        return UserFactory(
            local_authorization_repository=await test_container.get(
                LocalAuthorizationRepository
            ),
            refresh_token_manager=await test_container.get(RefreshTokenManager),
            access_token_manager=await test_container.get(AccessTokenManager),
            transaction_manager=await test_container.get(TransactionManager),
            session_repository=await test_container.get(SessionRepository),
            user_repository=await test_container.get(UserRepository),
        )


@pytest.fixture
async def container(config: Config) -> AsyncIterator[AsyncContainer]:
    class TestConnectionProvider(Provider):
        @provide(scope=Scope.APP)
        async def provide_async_engine(self) -> AsyncIterator[AsyncEngine]:
            engine = create_async_engine(config.database.url)
            yield engine
            await engine.dispose()

        @provide(scope=Scope.APP)
        def provide_async_sessionmaker(
            self,
            engine: AsyncEngine,
        ) -> async_sessionmaker[AsyncSession]:
            return async_sessionmaker(
                engine,
                expire_on_commit=False,
            )

        @provide(scope=Scope.REQUEST)
        async def provide_async_session(
            self,
            session_factory: async_sessionmaker[AsyncSession],
        ) -> AsyncIterator[AsyncSession]:
            async with session_factory() as session:
                yield session

    container = make_async_container(
        FastapiProvider(),
        ApplicationProvider(),
        TestConnectionProvider(),
        InfrastructureProvider(),
        CacheConnectionProvider(),
        context={
            APIConfig: config.api,
            DatabaseConfig: config.database,
            SecretsConfig: config.secrets,
            CacheConfig: config.cache,
        },
    )

    yield container
    await container.close()


@pytest.fixture
async def transport(container: AsyncContainer, config: Config) -> AsyncClient:
    app = create_app(config)
    setup_dishka(container, app)

    return AsyncClient(
        base_url="http://test.environment.org", transport=ASGITransport(app)
    )
