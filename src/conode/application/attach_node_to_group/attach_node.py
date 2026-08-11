from dataclasses import dataclass
from uuid import uuid4

from conode.application.errors import (
    NodeNotFoundError,
)
from conode.application.interfaces.repositories import (
    CompanyRepository,
    GroupRepository,
    NodeAssociationRepository,
    NodeRepository,
)
from conode.application.interfaces.transaction_manager import TransactionManager
from conode.application.services import AccessControlService
from conode.domain.group import GroupId
from conode.domain.node import NodeAssociation, NodeAssociationId, NodeId


@dataclass(frozen=True, slots=True, kw_only=True)
class AttachNodeRequestDTO:
    group_id: GroupId
    nodes: list[NodeId]


@dataclass
class AttachNodeInteractor:
    node_association_repository: NodeAssociationRepository
    access_control_service: AccessControlService
    transaction_manager: TransactionManager
    group_repository: GroupRepository
    node_repository: NodeRepository
    company_repository: CompanyRepository

    async def execute(self, request: AttachNodeRequestDTO) -> list[NodeAssociation]:
        user = await self.access_control_service.get_authorized_user()

        async with self.transaction_manager:
            group = await self.group_repository.get_by_id(request.group_id)

            request_nodes = set(request.nodes)
            existing_nodes = await self.node_repository.get_all_by_ids(
                list(request_nodes),
            )

            if len(existing_nodes) != len(request_nodes):
                raise NodeNotFoundError(
                    "Some of nodes not found",
                    [{"key": "node_ids", "value": list(request_nodes)}],
                )

            await self.access_control_service.ensure_user_can_manipulate_group(
                user,
                group,
            )

            associations = [
                NodeAssociation.new(
                    node_association_id=NodeAssociationId(uuid4()),
                    node=node,
                    group=group,
                )
                for node in existing_nodes
            ]

            await self.node_association_repository.create_all(associations)

            return associations
