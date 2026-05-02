from dishka import Provider, Scope, WithParents, provide_all

from conode.infrastructure.password_hasher import PasswordHasherImpl
from conode.infrastructure.token_manager import TokenManagerImpl
from conode.infrastructure.transaction_manager import TransactionManagerImpl


class InfrastructureProvider(Provider):
    provides = provide_all(
        WithParents[TransactionManagerImpl],
        WithParents[PasswordHasherImpl],
        WithParents[TokenManagerImpl],
        scope=Scope.REQUEST,
    )
