from dishka import Provider, Scope, WithParents, provide_all

from prodik.infrastructure.identity_provider import IdentityProviderImpl
from prodik.infrastructure.password_hasher import PasswordHasherImpl
from prodik.infrastructure.repositories import (
    LocalAuthorizationRepositoryImpl,
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
        WithParents[TransactionManagerImpl],
        WithParents[PasswordHasherImpl],
        WithParents[AccessTokenManagerImpl],
        WithParents[RefreshTokenManagerImpl],
        WithParents[LocalAuthorizationRepositoryImpl],
        WithParents[SessionRepositoryImpl],
        WithParents[UserRepositoryImpl],
        scope=Scope.REQUEST,
    )
