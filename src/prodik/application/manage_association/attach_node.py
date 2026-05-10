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
    NodeAssociationRepository,
    NodeRepository,
)
from prodik.application.interfaces.transaction_manager import TransactionManager
from prodik.application.services import AccessControlService
from prodik.domain.group import GroupId
from prodik.domain.node import NodeAssociation, NodeAssociationId, NodeId


@dataclass(frozen=True, slots=True, kw_only=True)
class AttachNodeRequestDTO:
    group_id: GroupId
    nodes: list[NodeId]


logger = structlog.get_logger()


@dataclass
class AttachNodeInteractor:
    node_association_repository: NodeAssociationRepository
    access_control_service: AccessControlService
    transaction_manager: TransactionManager
    group_repository: GroupRepository
    node_repository: NodeRepository
    company_repository: CompanyRepository

    async def execute(self, request: AttachNodeRequestDTO) -> list[NodeAssociation]:
        async with self.transaction_manager:
            user = await self.access_control_service.get_authorized_user()

            company = await self.company_repository.get_by_user_id(user.id)
            if company is None:
                raise CompanyNotFoundError("Company not found", None)

            group = await self.group_repository.get_by_id(request.group_id)
            if group is None:
                raise GroupNotFoundError("Group not found", None)

            existing_nodes = await self.node_repository.get_all_by_ids(
                list(set(request.nodes))
            )

            for node in existing_nodes:
                self.access_control_service.ensure_user_can_manipulate_node(
                    user,
                    company,
                    node,
                )

            associations = [
                NodeAssociation.new(
                    id=NodeAssociationId(uuid4()),
                    node=node,
                    group=group,
                    company=company,
                )
                for node in existing_nodes
            ]

            await self.node_association_repository.create_all(associations)

            return associations
