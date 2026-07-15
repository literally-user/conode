from dishka import Provider, Scope, WithParents, provide_all

from conode.infrastructure.token_manager import TokenManagerImpl


class SecretsProvider(Provider):
    provides = provide_all(
        WithParents[TokenManagerImpl],
        scope=Scope.REQUEST,
    )
