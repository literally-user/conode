from dishka import Provider, Scope, WithParents, provide_all

from conode.infrastructure.identity_provider import IdentityProviderImpl
from conode.infrastructure.password_hasher import PasswordHasherImpl
from conode.infrastructure.repositories import (
    AuthorizationRepositoryImpl,
    CompanyRepositoryImpl,
    ContextRepositoryImpl,
    ContractRepositoryImpl,
    EdgeRepositoryImpl,
    GroupRepositoryImpl,
    NodeAssociationRepositoryImpl,
    NodeRepositoryImpl,
    OfferContextRepositoryImpl,
    OfferGroupRepositoryImpl,
    OfferLinkRepositoryImpl,
    OfferRepositoryImpl,
    RolePermissionsRepositoryImpl,
    RoleRepositoryImpl,
    SessionRepositoryImpl,
    UserGrantRepositoryImpl,
    UserRepositoryImpl,
)
from conode.infrastructure.token_managers import (
    AccessTokenManagerImpl,
    RefreshTokenManagerImpl,
)


class InfrastructureProvider(Provider):
    provides = provide_all(
        WithParents[IdentityProviderImpl],
        WithParents[GroupRepositoryImpl],
        WithParents[PasswordHasherImpl],
        WithParents[NodeAssociationRepositoryImpl],
        WithParents[CompanyRepositoryImpl],
        WithParents[UserRepositoryImpl],
        WithParents[NodeRepositoryImpl],
        WithParents[AccessTokenManagerImpl],
        WithParents[RefreshTokenManagerImpl],
        WithParents[ContextRepositoryImpl],
        WithParents[EdgeRepositoryImpl],
        WithParents[UserGrantRepositoryImpl],
        WithParents[RoleRepositoryImpl],
        WithParents[RolePermissionsRepositoryImpl],
        WithParents[ContractRepositoryImpl],
        WithParents[OfferContextRepositoryImpl],
        WithParents[OfferGroupRepositoryImpl],
        WithParents[OfferLinkRepositoryImpl],
        WithParents[OfferRepositoryImpl],
        WithParents[AuthorizationRepositoryImpl],
        WithParents[SessionRepositoryImpl],
        scope=Scope.REQUEST,
    )
