import asyncio
from dataclasses import dataclass

from prodik.application.interfaces.repositories import (
    CompanyRepository,
    GroupRepository,
    NodeAssociationRepository,
    NodeRepository,
)
from prodik.application.interfaces.transaction_manager import TransactionManager
from prodik.application.services import AccessControlService
from prodik.domain.node import Node, NodeId


@dataclass(frozen=True, slots=True, kw_only=True)
class UpdateNodeRequestDTO:
    name: str
    description: str
    node_id: NodeId


@dataclass
class UpdateNodeInteractor:
    access_control_service: AccessControlService
    node_repository: NodeRepository
    company_repository: CompanyRepository
    node_association_repository: NodeAssociationRepository
    group_repository: GroupRepository
    transaction_manager: TransactionManager

    async def execute(self, request: UpdateNodeRequestDTO) -> Node:
        async with self.transaction_manager:
            user = await self.access_control_service.get_authorized_user()

            node = await self.node_repository.get_by_id(request.node_id)

            existing_associations = (
                await self.node_association_repository.get_all_by_node_id(node.id)
            )
            groups = await self.group_repository.get_all_by_ids(
                [association.group_id for association in existing_associations],
            )

            # TODO @LTU: Reduce useless connection using
            await asyncio.gather(
                *[
                    self.access_control_service.ensure_user_can_manipulate_group(
                        user,
                        group,
                    )
                    for group in groups
                ],
            )

            node.set_name(request.name)
            node.set_description(request.description)

            return node
