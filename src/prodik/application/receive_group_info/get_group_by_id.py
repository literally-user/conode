from dataclasses import dataclass

from prodik.application.errors import GroupNotFoundError
from prodik.application.interfaces.repositories import GroupRepository
from prodik.application.services import AccessControlService
from prodik.domain.group import Group, GroupId


@dataclass
class GetGroupByIdInteractor:
    access_control_service: AccessControlService
    group_repository: GroupRepository

    async def execute(self, group_id: GroupId) -> Group:
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

        return group
