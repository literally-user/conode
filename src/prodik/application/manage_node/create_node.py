from dataclasses import dataclass
from uuid import uuid4

from prodik.application.interfaces.repositories import (
    CompanyRepository,
    GroupRepository,
    NodeAssociationRepository,
    NodeRepository,
)
from prodik.application.interfaces.transaction_manager import TransactionManager
from prodik.application.services import AccessControlService
from prodik.domain.group import GroupId
from prodik.domain.node import Node, NodeAssociation, NodeAssociationId, NodeId


@dataclass(frozen=True, slots=True, kw_only=True)
class CreateNodeRequestDTO:
    name: str
    description: str
    group_id: GroupId


@dataclass
class CreateNodeInteractor:
    node_association_repository: NodeAssociationRepository
    company_repository: CompanyRepository
    group_repository: GroupRepository
    node_repository: NodeRepository
    transaction_manager: TransactionManager
    access_control_service: AccessControlService

    async def execute(self, request: CreateNodeRequestDTO) -> Node:
        async with self.transaction_manager:
            user = await self.access_control_service.get_authorized_user()

            group = await self.group_repository.get_by_id(request.group_id)
            company = await self.company_repository.get_by_id(group.company_id)

            await self.access_control_service.ensure_user_can_manipulate_group(
                user,
                group,
            )

            node = Node.new(
                node_id=NodeId(uuid4()),
                name=request.name,
                description=request.description,
                company=company,
            )

            association = NodeAssociation.new(
                node_association_id=NodeAssociationId(uuid4()),
                node=node,
                group=group,
            )

            await self.node_repository.create(node)
            await self.node_association_repository.create(association)

            return node
