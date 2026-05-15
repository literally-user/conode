import asyncio
from dataclasses import dataclass

from prodik.application.errors import (
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
from prodik.domain.node import NodeId


@dataclass
class DeleteNodeInteractor:
    transaction_manager: TransactionManager
    node_repository: NodeRepository
    company_repository: CompanyRepository
    node_association_repository: NodeAssociationRepository
    group_repository: GroupRepository
    access_control_service: AccessControlService

    async def execute(self, node_id: NodeId) -> None:
        async with self.transaction_manager:
            user = await self.access_control_service.get_authorized_user()

            node = await self.node_repository.get_by_id(node_id)
            if node is None:
                raise NodeNotFoundError(
                    "Node not found", [{"key": "node_id", "value": node_id}]
                )

            existing_associations = (
                await self.node_association_repository.get_all_by_node_id(node.id)
            )
            groups = await self.group_repository.get_all_by_ids(
                [association.group_id for association in existing_associations]
            )

            await asyncio.gather(
                *[
                    self.access_control_service.ensure_user_can_manipulate_group(
                        user,
                        group,
                    )
                    for group in groups
                ]
            )

            await self.node_repository.delete(node)
