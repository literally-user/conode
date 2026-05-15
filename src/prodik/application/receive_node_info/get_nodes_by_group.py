from dataclasses import dataclass

from prodik.application.errors import GroupNotFoundError
from prodik.application.interfaces.repositories import (
    CompanyRepository,
    GroupRepository,
    NodeAssociationRepository,
    NodeRepository,
)
from prodik.application.services import AccessControlService
from prodik.domain.group import GroupId
from prodik.domain.node import Node


@dataclass
class GetNodesByGroupInteractor:
    node_association_repository: NodeAssociationRepository
    access_control_service: AccessControlService
    company_repository: CompanyRepository
    group_repository: GroupRepository
    node_repository: NodeRepository

    async def execute(self, group_id: GroupId) -> list[Node]:
        user = await self.access_control_service.get_authorized_user()

        group = await self.group_repository.get_by_id(group_id)
        if group is None:
            raise GroupNotFoundError(
                "Group not found", [{"key": "group_id", "value": group_id}]
            )

        await self.access_control_service.ensure_user_can_view_group(
            user,
            group,
        )

        associations = await self.node_association_repository.get_all_by_group_id(
            group_id
        )

        return await self.node_repository.get_all_by_associations(associations)
