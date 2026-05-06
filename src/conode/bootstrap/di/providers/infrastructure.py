from dishka import Provider, Scope, WithParents, provide_all

from conode.infrastructure.identity_provider import IdentityProviderImpl
from conode.infrastructure.password_hasher import PasswordHasherImpl
from conode.infrastructure.repositories import (
    CompanyRepositoryImpl,
    LocalAuhthorizationRepositoryImpl,
    SessionRepositoryImpl,
    UserRepositoryImpl,
)
from conode.infrastructure.token_managers import (
    AccessTokenManagerImpl,
    RefreshTokenManagerImpl,
)
from conode.infrastructure.transaction_manager import TransactionManagerImpl


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
