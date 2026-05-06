from dishka import Provider, Scope, WithParents, provide_all

from prodik.infrastructure.identity_provider import IdentityProviderImpl
from prodik.infrastructure.password_hasher import PasswordHasherImpl
from prodik.infrastructure.repositories import (
    CompanyRepositoryImpl,
    LocalAuhthorizationRepositoryImpl,
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
        WithParents[LocalAuhthorizationRepositoryImpl],
        WithParents[SessionRepositoryImpl],
        WithParents[UserRepositoryImpl],
        WithParents[CompanyRepositoryImpl],
        WithParents[TransactionManagerImpl],
        WithParents[AccessTokenManagerImpl],
        WithParents[RefreshTokenManagerImpl],
        WithParents[PasswordHasherImpl],
        WithParents[IdentityProviderImpl],
        scope=Scope.REQUEST,
    )
