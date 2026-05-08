from dataclasses import dataclass
from uuid import uuid4

import structlog

from prodik.application.errors import (
    CompanyNotFoundError,
    GroupNotFoundError,
    UserNotFoundError,
)
from prodik.application.interfaces.identity_provider import IdentityProvider
from prodik.application.interfaces.repositories import (
    CompanyRepository,
    GroupRepository,
    NodeAssociationRepository,
    NodeRepository,
    UserRepository,
)
from prodik.application.interfaces.transaction_manager import TransactionManager
from prodik.application.services import AccessControlService
from prodik.domain.group import GroupId
from prodik.domain.node import Node, NodeAssociation, NodeAssociationId, NodeId

logger = structlog.get_logger()


@dataclass(frozen=True, slots=True, kw_only=True)
class CreateNodeRequestDTO:
    name: str
    description: str
    group_id: GroupId


@dataclass
class CreateNodeInteractor:
    node_association_repository: NodeAssociationRepository
    company_repository: CompanyRepository
    user_repository: UserRepository
    group_repository: GroupRepository
    node_repository: NodeRepository
    identity_provider: IdentityProvider
    transaction_manager: TransactionManager
    access_control_service: AccessControlService

    async def execute(self, request: CreateNodeRequestDTO) -> Node:
        async with self.transaction_manager:
            user_meta = self.identity_provider.get_current_user_meta()

            logger.info("Received user meta")

            user = await self.user_repository.get_by_id(user_meta["user_id"])
            if user is None:
                raise UserNotFoundError("User not found", None)

            logger.info("Received user", user_id=user.id)

            self.access_control_service.ensure_revision_is_valid(user_meta, user)

            company = await self.company_repository.get_by_user_id(user.id)
            if company is None:
                raise CompanyNotFoundError("User must have at least one company", None)

            group = await self.group_repository.get_by_id(request.group_id)
            if group is None:
                raise GroupNotFoundError("Group not found", None)

            node = Node.new(
                id=NodeId(uuid4()),
                name=request.name,
                description=request.description,
                company=company,
            )

            node_association = NodeAssociation.new(
                id=NodeAssociationId(uuid4()), node=node, group=group
            )

            await self.node_association_repository.create(node_association)
            await self.node_repository.create(node)

            return node
