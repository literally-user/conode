from collections.abc import AsyncIterator
from dataclasses import dataclass
from types import TracebackType
from unittest.mock import AsyncMock

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

from prodik.application.interfaces.password_hasher import PasswordHasher
from prodik.application.interfaces.repositories import (
    CompanyRepository,
    GroupRepository,
    LocalAuthorizationRepository,
    RolePermissionsRepository,
    RoleRepository,
    SessionRepository,
    UserGrantRepository,
    UserRepository,
)
from prodik.application.interfaces.token_managers import (
    AccessTokenManager,
    RefreshTokenManager,
)
from prodik.application.interfaces.transaction_manager import TransactionManager
from prodik.application.services import RoleManagmentService
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
from tests.factories.models import (
    CompanyFactory,
    GroupFactory,
    UserFactory,
)


@pytest.fixture(scope="session")
def config() -> Config:
    return load_config("test.config.toml")


@pytest.fixture(scope="session", autouse=True)
def startup() -> None:
    start_mapper()


@pytest.fixture
async def session_repository(container: AsyncContainer) -> SessionRepository:
    async with container() as test_container:
        return await test_container.get(SessionRepository)  # type: ignore[no-any-return]


@pytest.fixture
async def local_authorization_repository(
    container: AsyncContainer,
) -> LocalAuthorizationRepository:
    async with container() as test_container:
        return await test_container.get(LocalAuthorizationRepository)  # type: ignore[no-any-return]


@pytest.fixture
async def group_repository(
    container: AsyncContainer,
) -> GroupRepository:
    async with container() as test_container:
        return await test_container.get(GroupRepository)  # type: ignore[no-any-return]


@pytest.fixture
async def access_token_manager(container: AsyncContainer) -> AccessTokenManager:
    async with container() as test_container:
        return await test_container.get(AccessTokenManager)  # type: ignore[no-any-return]


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
async def role_repository(container: AsyncContainer) -> RoleRepository:
    async with container() as test_container:
        return await test_container.get(RoleRepository)  # type: ignore[no-any-return]


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
