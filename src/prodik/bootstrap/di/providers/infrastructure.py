from dishka import Provider, Scope, WithParents, provide_all

from prodik.infrastructure.password_hasher import PasswordHasherImpl
from prodik.infrastructure.token_manager import TokenManagerImpl
from prodik.infrastructure.transaction_manager import TransactionManagerImpl


class InfrastructureProvider(Provider):
    provides = provide_all(
        WithParents[TransactionManagerImpl],
        WithParents[PasswordHasherImpl],
        WithParents[TokenManagerImpl],
        scope=Scope.REQUEST,
    )
