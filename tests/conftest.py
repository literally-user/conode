from collections.abc import AsyncGenerator
from typing import cast
from unittest.mock import AsyncMock

import pytest
from dishka import AsyncContainer, Provider, Scope, make_async_container, provide
from dishka.integrations.fastapi import FastapiProvider, setup_dishka
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from prodik.application.interfaces.password_hasher import PasswordHasher
from prodik.application.interfaces.repositories import (
    CompanyRepository,
    ContextRepository,
    EdgeRepository,
    GroupRepository,
    LocalAuthorizationRepository,
    NodeAssociationRepository,
    NodeRepository,
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
from tests.factories import (
    CompanyFactory,
    ContextFactory,
    EdgeFactory,
    GroupFactory,
    NodeAssociationFactory,
    NodeFactory,
    UserFactory,
)
from tests.services import EntityExistenceService


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
async def user_repository(test_container: AsyncContainer) -> UserRepository:
    async with test_container() as container:
        return cast("UserRepository", await container.get(UserRepository))


@pytest.fixture
async def company_repository(test_container: AsyncContainer) -> CompanyRepository:
    async with test_container() as container:
        return cast("CompanyRepository", await container.get(CompanyRepository))


@pytest.fixture
async def context_repository(test_container: AsyncContainer) -> ContextRepository:
    async with test_container() as container:
        return cast("ContextRepository", await container.get(ContextRepository))


@pytest.fixture
async def edge_repository(test_container: AsyncContainer) -> EdgeRepository:
    async with test_container() as container:
        return cast("EdgeRepository", await container.get(EdgeRepository))


@pytest.fixture
async def group_repository(test_container: AsyncContainer) -> GroupRepository:
    async with test_container() as container:
        return cast("GroupRepository", await container.get(GroupRepository))


@pytest.fixture
async def group_factory(
    test_container: AsyncContainer, company_factory: CompanyFactory
) -> GroupFactory:
    async with test_container() as container:
        return GroupFactory(
            group_repository=await container.get(GroupRepository),
            company_factory=company_factory,
        )


@pytest.fixture
async def context_factory(
    test_container: AsyncContainer, company_factory: CompanyFactory
) -> ContextFactory:
    async with test_container() as container:
        return ContextFactory(
            context_repository=await container.get(ContextRepository),
            company_factory=company_factory,
        )


@pytest.fixture
async def edge_factory(test_container: AsyncContainer) -> EdgeFactory:
    async with test_container() as container:
        return EdgeFactory(
            edge_repository=await container.get(EdgeRepository),
        )


@pytest.fixture
async def node_factory(
    test_container: AsyncContainer, company_factory: CompanyFactory
) -> NodeFactory:
    async with test_container() as container:
        return NodeFactory(
            node_repository=await container.get(NodeRepository),
            company_factory=company_factory,
        )


@pytest.fixture
async def node_association_factory(
    test_container: AsyncContainer,
) -> NodeAssociationFactory:
    async with test_container() as container:
        return NodeAssociationFactory(
            node_association_repository=await container.get(NodeAssociationRepository),
        )


@pytest.fixture
async def node_association_repository(
    test_container: AsyncContainer,
) -> NodeAssociationRepository:
    async with test_container() as container:
        return cast(
            "NodeAssociationRepository",
            await container.get(NodeAssociationRepository),
        )


@pytest.fixture
async def entity_existence_service(
    test_session: AsyncSession,
) -> EntityExistenceService:
    return EntityExistenceService(session=test_session)


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
