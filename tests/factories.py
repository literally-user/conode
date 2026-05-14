import asyncio
import random
import string
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Annotated
from uuid import uuid4

import structlog
from polyfactory.factories.pydantic_factory import ModelFactory
from pydantic import BaseModel, EmailStr, Field

from prodik.application.interfaces.password_hasher import PasswordHasher
from prodik.application.interfaces.repositories import (
    CompanyRepository,
    ContextRepository,
    EdgeRepository,
    GroupRepository,
    LocalAuthorizationRepository,
    NodeAssociationRepository,
    NodeRepository,
    OfferContextRepository,
    OfferGroupRepository,
    OfferLinkRepository,
    OfferRepository,
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
from prodik.domain.authorization import (
    LocalAuthorization,
    LocalAuthorizationId,
    Session,
    SessionId,
)
from prodik.domain.company import Company, CompanyId
from prodik.domain.context import Context, ContextId
from prodik.domain.edge import Edge, EdgeId
from prodik.domain.grant import UserGrant, UserGrantId
from prodik.domain.group import Group, GroupId
from prodik.domain.node import Node, NodeAssociation, NodeAssociationId, NodeId
from prodik.domain.offer import (
    Offer,
    OfferContext,
    OfferContextId,
    OfferGroup,
    OfferGroupId,
    OfferId,
    OfferLink,
    OfferLinkId,
)
from prodik.domain.role import (
    EntityType,
    PermissionType,
    Role,
    RoleId,
    RolePermission,
    RolePermissionEntityId,
    RolePermissionId,
)
from prodik.domain.role.model import (
    MAX_ALLOWED_ROLE_NAME_LENGTH,
    MIN_ALLOWED_ROLE_NAME_LENGTH,
)
from prodik.domain.user import User, UserId, UserSystemRole


class CreatePermissionRequest(BaseModel):
    permission: PermissionType
    entity_type: EntityType
    entity_id: RolePermissionEntityId


class CreateRoleRequest(BaseModel):
    name: Annotated[
        str,
        Field(
            min_length=MIN_ALLOWED_ROLE_NAME_LENGTH,
            max_length=MAX_ALLOWED_ROLE_NAME_LENGTH,
        ),
    ]
    company_id: CompanyId
    permissions: list[CreatePermissionRequest]


class RegisterRequest(BaseModel):
    username: Annotated[str, Field(min_length=5, max_length=30)]
    first_name: Annotated[str, Field(min_length=1, max_length=30)]
    last_name: Annotated[str, Field(min_length=1, max_length=30)]
    password: Annotated[str, Field(min_length=7, max_length=100)]
    email: EmailStr


class CreatePermissionRequestFactory(ModelFactory[CreatePermissionRequest]):
    __model__ = CreatePermissionRequest


class CreateRoleRequestFactory(ModelFactory[CreateRoleRequest]):
    __model__ = CreateRoleRequest


class RegisterRequestFactory(ModelFactory[RegisterRequest]):
    __model__ = RegisterRequest


class RegisterCompanyRequest(BaseModel):
    name: Annotated[str, Field(min_length=1, max_length=50)]
    description: Annotated[str, Field(min_length=20, max_length=3000)]


class RegisterCompanyRequestFactory(ModelFactory[RegisterCompanyRequest]):
    __model__ = RegisterCompanyRequest


logger = structlog.get_logger()


def generate_random_string(length: int = 5) -> str:
    return "".join(random.choices(string.ascii_lowercase, k=length))  # noqa: S311


@dataclass
class UserFactoryResponse:
    user: User
    session: Session
    authorization: LocalAuthorization
    access_token: str
    refresh_token: str
    password: str


@dataclass(slots=True)
class UserFactory:
    password_hasher: PasswordHasher
    access_token_manager: AccessTokenManager
    refresh_token_manager: RefreshTokenManager
    user_repository: UserRepository
    session_repository: SessionRepository
    authorization_repository: LocalAuthorizationRepository

    async def create_user(self, *, admin: bool = False) -> UserFactoryResponse:
        user = User.new(
            id=UserId(uuid4()),
            username=generate_random_string(10),
            first_name=generate_random_string(10),
            last_name=generate_random_string(10),
            email=generate_random_string(10) + "@conode.team",
            bio=generate_random_string(100),
        )

        if admin:
            user.system_role = UserSystemRole.ADMIN

        password = generate_random_string(10)
        hashed_password = self.password_hasher.hash(password)
        access_token, _ = self.access_token_manager.encode(user)
        refresh_token = self.refresh_token_manager.encode()

        authorization = LocalAuthorization.new(
            id=LocalAuthorizationId(uuid4()),
            password=hashed_password,
            user=user,
        )

        session = Session.new(
            id=SessionId(uuid4()),
            user=user,
            host="127.0.0.1",
            token=refresh_token,
        )

        await self.user_repository.create(user)
        await asyncio.gather(
            self.session_repository.create(session),
            self.authorization_repository.create(authorization),
        )

        return UserFactoryResponse(
            user=user,
            session=session,
            authorization=authorization,
            access_token=access_token,
            refresh_token=refresh_token,
            password=password,
        )


@dataclass(slots=True)
class CompanyFactory:
    role_repository: RoleRepository
    role_permissions_repository: RolePermissionsRepository
    user_grant_repository: UserGrantRepository
    company_repository: CompanyRepository
    user_factory: UserFactory

    async def create_company(self, user: User | None = None) -> Company:
        if user is None:
            user = (await self.user_factory.create_user(admin=False)).user

        company = Company.new(
            id=CompanyId(uuid4()),
            name=generate_random_string(10),
            description=generate_random_string(300),
            owner=user,
        )

        role = Role.new(id=RoleId(uuid4()), name="owner", company=company)

        permissions = [
            RolePermission.new(
                id=RolePermissionId(uuid4()),
                role=role,
                permission=PermissionType.READ,
                entity_type=EntityType.COMPANY,
                entity_id=company.id,
            ),
            RolePermission.new(
                id=RolePermissionId(uuid4()),
                role=role,
                permission=PermissionType.MODIFY,
                entity_type=EntityType.COMPANY,
                entity_id=company.id,
            ),
        ]

        grant = UserGrant.new(
            id=UserGrantId(uuid4()),
            role=role,
            user=user,
        )

        await self.company_repository.create(company)
        await self.role_repository.create(role)
        await asyncio.gather(
            self.role_permissions_repository.create_all(permissions),
            self.user_grant_repository.create(grant),
        )

        return company


@dataclass(slots=True)
class GroupFactory:
    group_repository: GroupRepository
    company_factory: CompanyFactory

    async def create_group(
        self, company: Company | None = None, parent_group: Group | None = None
    ) -> Group:
        group = Group.new(
            id=GroupId(uuid4()),
            name=generate_random_string(10),
            description=generate_random_string(30),
            company=company or await self.company_factory.create_company(),
            parent_group=parent_group,
        )
        await self.group_repository.create(group)
        return group


@dataclass(slots=True)
class RoleFactory:
    role_repository: RoleRepository
    role_permissions_repository: RolePermissionsRepository

    async def create_role(
        self,
        *,
        company: Company,
        name: str | None = None,
        with_permissions: bool = True,
        permission_entity_id: RolePermissionEntityId | None = None,
    ) -> Role:

        role = Role.new(
            id=RoleId(uuid4()),
            name=name or generate_random_string(10),
            company=company,
        )

        permissions: list[RolePermission] = []

        if with_permissions:
            entity_id = permission_entity_id or company.id

            permissions = [
                RolePermission.new(
                    id=RolePermissionId(uuid4()),
                    role=role,
                    permission=PermissionType.READ,
                    entity_type=EntityType.COMPANY,
                    entity_id=entity_id,
                ),
                RolePermission.new(
                    id=RolePermissionId(uuid4()),
                    role=role,
                    permission=PermissionType.MODIFY,
                    entity_type=EntityType.COMPANY,
                    entity_id=entity_id,
                ),
            ]

        await self.role_repository.create(role)

        if permissions:
            await self.role_permissions_repository.create_all(permissions)

        return role


@dataclass(slots=True)
class NodeAssociationFactory:
    node_association_repository: NodeAssociationRepository

    async def create_association(self, node: Node, group: Group) -> NodeAssociation:
        association = NodeAssociation.new(
            id=NodeAssociationId(uuid4()),
            node=node,
            group=group,
        )
        await self.node_association_repository.create(association)
        return association


@dataclass(slots=True)
class NodeFactory:
    group_factory: GroupFactory
    node_association_factory: NodeAssociationFactory
    node_repository: NodeRepository
    user_factory: UserFactory
    company_factory: CompanyFactory

    async def create_node(
        self,
        association: NodeAssociation | None = None,
        company: Company | None = None,
        group: Group | None = None,
        user: User | None = None,
    ) -> Node:
        if user is None:
            user = (await self.user_factory.create_user(admin=False)).user
        if company is None:
            company = await self.company_factory.create_company(user)

        node = Node.new(
            id=NodeId(uuid4()),
            name=generate_random_string(10),
            description=generate_random_string(30),
            company=company,
        )

        if group is None:
            group = await self.group_factory.create_group(company)

        await self.node_repository.create(node)

        if association is None:
            association = await self.node_association_factory.create_association(
                node, group
            )

        return node


@dataclass(slots=True)
class ContextFactory:
    context_repository: ContextRepository
    company_factory: CompanyFactory

    async def create_context(self, company: Company | None = None) -> Context:
        context = Context.new(
            id=ContextId(uuid4()),
            name=generate_random_string(10),
            description=generate_random_string(30),
            company=company or await self.company_factory.create_company(),
        )

        await self.context_repository.create(context)

        return context


@dataclass(slots=True)
class EdgeFactory:
    edge_repository: EdgeRepository

    async def create_edge(
        self,
        node_a: Node,
        node_b: Node,
        company: Company,
        context: Context,
        weight: float = 0,
    ) -> Edge:
        edge = Edge.new(
            id=EdgeId(uuid4()),
            node_a=node_a,
            node_b=node_b,
            company=company,
            context=context,
            weight=weight,
        )
        await self.edge_repository.create(edge)
        return edge


@dataclass(slots=True)
class OfferLinkFactory:
    offer_link_repository: OfferLinkRepository

    async def create_link(
        self,
        *,
        request_offer: Offer,
        response_offer: Offer,
    ) -> OfferLink:
        offer_link = OfferLink.new(
            id=OfferLinkId(uuid4()),
            request_offer=request_offer,
            response_offer=response_offer,
        )

        await self.offer_link_repository.create(offer_link)

        return offer_link


@dataclass(slots=True)
class OfferFactory:
    offer_repository: OfferRepository
    offer_group_repository: OfferGroupRepository
    offer_context_repository: OfferContextRepository

    offer_link_factory: OfferLinkFactory

    company_factory: CompanyFactory
    group_factory: GroupFactory
    context_factory: ContextFactory

    async def create_offer(
        self,
        *,
        from_company: Company | None = None,
        to_company: Company | None = None,
        from_offer: Offer | None = None,
        requires_counteroffer: bool = False,
        groups: dict[GroupId, PermissionType | str] | None = None,
        contexts: dict[ContextId, PermissionType | str] | None = None,
    ) -> Offer:
        if from_company is None:
            from_company = await self.company_factory.create_company()

        if to_company is None:
            to_company = await self.company_factory.create_company()

        offer = Offer.new(
            id=OfferId(uuid4()),
            title=generate_random_string(15),
            description=generate_random_string(100),
            from_company=from_company,
            to_company=to_company,
            from_offer=from_offer,
            expires_in=datetime.now(UTC) + timedelta(days=7),
            requires_counteroffer=requires_counteroffer,
        )

        await self.offer_repository.create(offer)

        offer_groups: list[OfferGroup] = []
        offer_contexts: list[OfferContext] = []

        if groups is None:
            default_group = await self.group_factory.create_group(company=from_company)
            groups = {
                default_group.id: PermissionType.READ,
            }

        if contexts is None:
            default_context = await self.context_factory.create_context(
                company=from_company
            )
            contexts = {
                default_context.id: PermissionType.READ,
            }

        for group_id, permission in groups.items():
            permission_type = (
                PermissionType(permission)
                if isinstance(permission, str)
                else permission
            )

            offer_groups.append(
                OfferGroup(
                    id=OfferGroupId(uuid4()),
                    offer_id=offer.id,
                    group_id=group_id,
                    permission_type=permission_type,
                    created_at=datetime.now(UTC),
                    updated_at=datetime.now(UTC),
                )
            )

        for context_id, permission in contexts.items():
            permission_type = (
                PermissionType(permission)
                if isinstance(permission, str)
                else permission
            )

            offer_contexts.append(
                OfferContext(
                    id=OfferContextId(uuid4()),
                    offer_id=offer.id,
                    context_id=context_id,
                    permission_type=permission_type,
                    created_at=datetime.now(UTC),
                    updated_at=datetime.now(UTC),
                )
            )

        await asyncio.gather(
            self.offer_group_repository.create_all(offer_groups),
            self.offer_context_repository.create_all(offer_contexts),
        )

        return offer

    async def create_counter_offer(
        self,
        *,
        from_company: Company,
        to_company: Company,
        from_offer: Offer,
        groups: dict[GroupId, PermissionType | str] | None = None,
        contexts: dict[ContextId, PermissionType | str] | None = None,
    ) -> Offer:
        counter_offer = await self.create_offer(
            from_company=from_company,
            to_company=to_company,
            from_offer=from_offer,
            requires_counteroffer=True,
            groups=groups,
            contexts=contexts,
        )

        await self.offer_link_factory.create_link(
            request_offer=from_offer,
            response_offer=counter_offer,
        )

        return counter_offer

    async def create_counter_offer_without_link(
        self,
        *,
        from_company: Company,
        to_company: Company,
        from_offer: Offer,
        groups: dict[GroupId, PermissionType | str] | None = None,
        contexts: dict[ContextId, PermissionType | str] | None = None,
    ) -> Offer:
        return await self.create_offer(
            from_company=from_company,
            to_company=to_company,
            from_offer=from_offer,
            requires_counteroffer=True,
            groups=groups,
            contexts=contexts,
        )
