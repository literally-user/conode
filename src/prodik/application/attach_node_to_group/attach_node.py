from dataclasses import dataclass
from uuid import uuid4

from prodik.application.errors import (
    GroupNotFoundError,
    NodeCannotHaveSameAssociationsError,
    NodeNotFoundError,
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

            group = await self.group_repository.get_by_id(request.group_id)
            if group is None:
                raise GroupNotFoundError(
                    "Group not found", [{"key": "group_id", "value": request.group_id}]
                )

            request_nodes = set(request.nodes)
            existing_nodes = await self.node_repository.get_all_by_ids(
                list(request_nodes)
            )

            if len(existing_nodes) != len(request_nodes):
                raise NodeNotFoundError(
                    "Some of nodes not found",
                    [{"key": "node_ids", "value": list(request_nodes)}],
                )

            existing_associations = (
                await self.node_association_repository.get_all_by_group_id(
                    request.group_id
                )
            )

            await self.access_control_service.ensure_user_can_manipulate_group(
                user,
                group,
            )

            existing_node_ids = {a.node_id for a in existing_associations}

            for node in existing_nodes:
                if node.id in existing_node_ids:
                    raise NodeCannotHaveSameAssociationsError(
                        "Node cannot have same associations",
                        [
                            {"key": "node_id", "value": node.id},
                            {"key": "group_id", "value": group.id},
                        ],
                    )

            associations = [
                NodeAssociation.new(
                    id=NodeAssociationId(uuid4()),
                    node=node,
                    group=group,
                )
                for node in existing_nodes
            ]

            await self.node_association_repository.create_all(associations)

            return associations
