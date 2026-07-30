from collections.abc import AsyncIterator
from dataclasses import dataclass
from types import TracebackType
from unittest.mock import AsyncMock

import jwt
import pytest
from dishka import (
    AsyncContainer,
    Provider,
    Scope,
    WithParents,
    make_async_container,
    provide,
    provide_all,
)
from dishka.integrations.fastapi import FastapiProvider, setup_dishka
from httpx import ASGITransport, AsyncClient
from sqlalchemy import URL
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
)

from conode.application.interfaces.password_hasher import PasswordHasher
from conode.application.interfaces.repositories import (
    CompanyRepository,
    ContextRepository,
    EdgeRepository,
    GroupRepository,
    NodeAssociationRepository,
    NodeRepository,
    RolePermissionsRepository,
    RoleRepository,
    UserGrantRepository,
    UserRepository,
)
from conode.application.interfaces.token_manager import (
    TokenManager,
    UserMeta,
)
from conode.application.interfaces.transaction_manager import TransactionManager
from conode.application.services import RoleManagmentService
from conode.bootstrap.api.run import create_app
from conode.bootstrap.di.providers import (
    ApplicationProvider,
    InfrastructureProvider,
)
from conode.domain.user import User, UserSystemRole
from conode.infrastructure.config import (
    APIConfig,
    Config,
    DatabaseConfig,
    SecretsConfig,
    load_config,
)
from conode.infrastructure.persistence import start_mapper
from tests.factories.models import (
    CompanyFactory,
    ContextFactory,
    EdgeFactory,
    GroupFactory,
    NodeAssociationFactory,
    NodeFactory,
    UserFactory,
)


@dataclass
class MockTokenManager(TokenManager):
    config: SecretsConfig

    def decode(self, token: str) -> UserMeta:
        payload = jwt.decode(
            token,
            key=self.config.secret,
            algorithms=["HS256"],
        )
        role = UserSystemRole.USER
        if "realm-admin" in payload["resource_access"]["realm-management"]["roles"]:
            role = UserSystemRole.ADMIN

        return UserMeta(
            email=payload["email"],
            first_name=payload["given_name"],
            last_name=payload["family_name"],
            username=payload["preferred_username"],
            system_role=role,
        )

    def encode(self, user: User, *, admin: bool = False) -> str:
        return jwt.encode(
            payload={
                "email": user.email.value,
                "given_name": user.first_name.value,
                "family_name": user.last_name.value,
                "preferred_username": user.username.value,
                "resource_access": {
                    "realm-management": {"roles": ["realm-admin" if admin else "user"]}
                },
            },
            algorithm="HS256",
            key=self.config.secret,
        )


@pytest.fixture(scope="session")
def config() -> Config:
    return load_config("test.config.toml")


@pytest.fixture(scope="session", autouse=True)
def startup() -> None:
    start_mapper()


@pytest.fixture
async def node_repository(
    container: AsyncContainer,
) -> NodeRepository:
    async with container() as test_container:
        return await test_container.get(NodeRepository)  # type: ignore[no-any-return]


@pytest.fixture
async def node_association_repository(
    container: AsyncContainer,
) -> NodeAssociationRepository:
    async with container() as test_container:
        return await test_container.get(NodeAssociationRepository)  # type: ignore[no-any-return]


@pytest.fixture
async def group_repository(
    container: AsyncContainer,
) -> GroupRepository:
    async with container() as test_container:
        return await test_container.get(GroupRepository)  # type: ignore[no-any-return]


@pytest.fixture
async def user_repository(container: AsyncContainer) -> UserRepository:
    async with container() as test_container:
        return await test_container.get(UserRepository)  # type: ignore[no-any-return]


@pytest.fixture
async def user_grant_repository(container: AsyncContainer) -> UserGrantRepository:
    async with container() as test_container:
        return await test_container.get(UserGrantRepository)  # type: ignore[no-any-return]


@pytest.fixture
async def company_repository(container: AsyncContainer) -> CompanyRepository:
    async with container() as test_contaner:
        return await test_contaner.get(CompanyRepository)  # type: ignore[no-any-return]


@pytest.fixture
async def context_repository(container: AsyncContainer) -> ContextRepository:
    async with container() as test_container:
        return await test_container.get(ContextRepository)  # type: ignore[no-any-return]


@pytest.fixture
async def edge_repository(container: AsyncContainer) -> EdgeRepository:
    async with container() as test_contaner:
        return await test_contaner.get(EdgeRepository)  # type: ignore[no-any-return]


@pytest.fixture
async def role_repository(container: AsyncContainer) -> RoleRepository:
    async with container() as test_container:
        return await test_container.get(RoleRepository)  # type: ignore[no-any-return]


@pytest.fixture
async def node_factory(container: AsyncContainer) -> NodeFactory:
    async with container() as test_container:
        return NodeFactory(
            node_repository=await test_container.get(NodeRepository),
            transaction_manager=await test_container.get(TransactionManager),
            node_association_repository=await test_container.get(
                NodeAssociationRepository
            ),
        )


@pytest.fixture
async def node_association_factory(container: AsyncContainer) -> NodeAssociationFactory:
    async with container() as test_container:
        return NodeAssociationFactory(
            transaction_manager=await test_container.get(TransactionManager),
            node_association_repository=await test_container.get(
                NodeAssociationRepository
            ),
        )


@pytest.fixture
async def edge_factory(container: AsyncContainer) -> EdgeFactory:
    async with container() as test_container:
        return EdgeFactory(
            transaction_manager=await test_container.get(TransactionManager),
            edge_repository=await test_container.get(
                EdgeRepository,
            ),
        )


@pytest.fixture
async def context_factory(container: AsyncContainer) -> ContextFactory:
    async with container() as test_container:
        return ContextFactory(
            transaction_manager=await test_container.get(TransactionManager),
            context_repository=await test_container.get(ContextRepository),
        )


@pytest.fixture
async def user_factory(container: AsyncContainer) -> UserFactory:
    async with container() as test_container:
        return UserFactory(
            token_manager=await test_container.get(TokenManager),
            transaction_manager=await test_container.get(TransactionManager),
            password_hasher=await test_container.get(PasswordHasher),
            user_repository=await test_container.get(UserRepository),
        )


@pytest.fixture
async def group_factory(container: AsyncContainer) -> GroupFactory:
    async with container() as test_container:
        return GroupFactory(
            group_repository=await test_container.get(GroupRepository),
            transaction_manager=await test_container.get(TransactionManager),
        )


@pytest.fixture
async def company_factory(container: AsyncContainer) -> CompanyFactory:
    async with container() as test_container:
        return CompanyFactory(
            role_permissions_repository=await test_container.get(
                RolePermissionsRepository
            ),
            role_managment_service=await test_container.get(RoleManagmentService),
            user_grant_repository=await test_container.get(UserGrantRepository),
            transaction_manager=await test_container.get(TransactionManager),
            company_repository=await test_container.get(CompanyRepository),
            role_repository=await test_container.get(RoleRepository),
        )


@pytest.fixture
async def session(config: Config) -> AsyncIterator[AsyncSession]:
    engine = create_async_engine(
        url=URL.create(
            "postgresql+asyncpg",
            username=config.database.username,
            password=config.database.password,
            database=config.database.database,
            port=config.database.port,
            host=config.database.host,
        ),
        pool_size=5,
        max_overflow=96,
        pool_timeout=30,
    )

    async with AsyncSession(engine) as session:
        session.commit = AsyncMock()  # type: ignore
        yield session
        await session.close()


@dataclass
class TestTransactionManagerImpl(TransactionManager):
    session: AsyncSession

    async def __aenter__(self) -> None:
        self.tx = await self.session.begin_nested()

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        await self.tx.__aexit__(exc_type, exc, tb)


@pytest.fixture
async def container(
    config: Config, session: AsyncSession
) -> AsyncIterator[AsyncContainer]:
    class TestConnectionProvider(Provider):
        provides = provide_all(
            WithParents[TestTransactionManagerImpl], scope=Scope.REQUEST
        )

        @provide(scope=Scope.REQUEST)
        async def provide_async_session(self) -> AsyncSession:
            return session

    class TestSecretsProvider(Provider):
        provides = provide_all(WithParents[MockTokenManager], scope=Scope.REQUEST)

    container = make_async_container(
        FastapiProvider(),
        ApplicationProvider(),
        TestConnectionProvider(),
        InfrastructureProvider(),
        TestSecretsProvider(),
        context={
            APIConfig: config.api,
            DatabaseConfig: config.database,
            SecretsConfig: config.secrets,
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
