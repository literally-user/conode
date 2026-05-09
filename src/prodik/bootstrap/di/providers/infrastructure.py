from dishka import Provider, Scope, WithParents, provide_all

from prodik.infrastructure.identity_provider import IdentityProviderImpl
from prodik.infrastructure.password_hasher import PasswordHasherImpl
from prodik.infrastructure.repositories import (
    CompanyRepositoryImpl,
    ContextRepositoryImpl,
    EdgeRepositoryImpl,
    GroupRepositoryImpl,
    LocalAuthorizationRepositoryImpl,
    NodeAssociationRepositoryImpl,
    NodeRepositoryImpl,
    SessionRepositoryImpl,
    UserRepositoryImpl,
)
from prodik.infrastructure.token_managers import (
    AccessTokenManagerImpl,
    RefreshTokenManagerImpl,
)
from prodik.infrastructure.transaction_manager import TransactionManagerImpl


class InfrastructureProvider(Provider):
    provides = provide_all(
        WithParents[IdentityProviderImpl],
        WithParents[GroupRepositoryImpl],
        WithParents[TransactionManagerImpl],
        WithParents[PasswordHasherImpl],
        WithParents[AccessTokenManagerImpl],
        WithParents[RefreshTokenManagerImpl],
        WithParents[NodeAssociationRepositoryImpl],
        WithParents[LocalAuthorizationRepositoryImpl],
        WithParents[SessionRepositoryImpl],
        WithParents[CompanyRepositoryImpl],
        WithParents[UserRepositoryImpl],
        WithParents[NodeRepositoryImpl],
        WithParents[ContextRepositoryImpl],
        WithParents[EdgeRepositoryImpl],
        scope=Scope.REQUEST,
    )
