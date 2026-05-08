from collections.abc import AsyncGenerator
from unittest.mock import AsyncMock

import pytest
from dishka import AsyncContainer, Provider, Scope, make_async_container, provide
from dishka.integrations.fastapi import FastapiProvider, setup_dishka
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from prodik.application.interfaces.password_hasher import PasswordHasher
from prodik.application.interfaces.repositories import (
    CompanyRepository,
    LocalAuthorizationRepository,
    SessionRepository,
    UserRepository,
)
from prodik.application.interfaces.token_managers import (
    AccessTokenManager,
    RefreshTokenManager,
)
from prodik.bootstrap.api import create_app
from prodik.bootstrap.di.providers import ApplicationProvider, InfrastructureProvider
from prodik.infrastructure.config import (
    APIConfig,
    Config,
    DatabaseConfig,
    SecretsConfig,
    load_config,
)
from prodik.infrastructure.persistence import start_mapper
from tests.factories import CompanyFactory, UserFactory


@pytest.fixture(scope="session")
def test_config() -> Config:
    return load_config("test.config.toml")


@pytest.fixture(scope="session", autouse=True)
def startup() -> None:
    start_mapper()


@pytest.fixture
async def user_factory(test_container: AsyncContainer) -> UserFactory:
    async with test_container() as container:
        return UserFactory(
            password_hasher=await container.get(PasswordHasher),
            access_token_manager=await container.get(AccessTokenManager),
            refresh_token_manager=await container.get(RefreshTokenManager),
            user_repository=await container.get(UserRepository),
            session_repository=await container.get(SessionRepository),
            authorization_repository=await container.get(LocalAuthorizationRepository),
        )


@pytest.fixture
async def company_factory(
    test_container: AsyncContainer, user_factory: UserFactory
) -> CompanyFactory:
    async with test_container() as container:
        return CompanyFactory(
            company_repository=await container.get(CompanyRepository),
            user_factory=user_factory,
        )


@pytest.fixture
async def test_session(test_config: Config) -> AsyncGenerator[AsyncSession]:
    engine = create_async_engine(test_config.database.url)
    async with engine.begin() as conn, AsyncSession(conn) as session:
        session.commit = AsyncMock()  # type: ignore
        yield session
        await session.rollback()


@pytest.fixture
async def test_container(
    test_session: AsyncSession, test_config: Config
) -> AsyncGenerator[AsyncContainer]:
    class TestConnectionProvider(Provider):
        @provide(scope=Scope.REQUEST)
        async def session(self) -> AsyncSession:
            return test_session

    container = make_async_container(
        FastapiProvider(),
        InfrastructureProvider(),
        ApplicationProvider(),
        TestConnectionProvider(),
        context={
            APIConfig: test_config.api,
            DatabaseConfig: test_config.database,
            SecretsConfig: test_config.secrets,
        },
    )

    yield container

    await container.close()


@pytest.fixture
async def test_client(
    test_config: Config, test_container: AsyncContainer
) -> AsyncGenerator[AsyncClient]:
    app = create_app(test_config)
    setup_dishka(app=app, container=test_container)

    async with AsyncClient(
        base_url="http://test.localhost.com", transport=ASGITransport(app)
    ) as client:
        yield client
