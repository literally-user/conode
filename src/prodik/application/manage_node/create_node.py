from dataclasses import dataclass
from uuid import uuid4

import structlog

from prodik.application.errors import (
    CompanyNotFoundError,
    GroupNotFoundError,
)
from prodik.application.interfaces.repositories import (
    CompanyRepository,
    GroupRepository,
    NodeRepository,
)
from prodik.application.interfaces.transaction_manager import TransactionManager
from prodik.application.services import AccessControlService
from prodik.domain.group import GroupId
from prodik.domain.node import Node, NodeId

logger = structlog.get_logger()


@dataclass(frozen=True, slots=True, kw_only=True)
class CreateNodeRequestDTO:
    name: str
    description: str
    group_id: GroupId


@dataclass
class CreateNodeInteractor:
    company_repository: CompanyRepository
    group_repository: GroupRepository
    node_repository: NodeRepository
    transaction_manager: TransactionManager
    access_control_service: AccessControlService

    async def execute(self, request: CreateNodeRequestDTO) -> Node:
        async with self.transaction_manager:
            user = await self.access_control_service.get_authorized_user()

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

            await self.node_repository.create(node)

            return node
