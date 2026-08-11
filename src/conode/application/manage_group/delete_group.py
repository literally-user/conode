from dataclasses import dataclass

from conode.application.interfaces.repositories import (
    CompanyRepository,
    GroupRepository,
)
from conode.application.interfaces.transaction_manager import TransactionManager
from conode.application.services import AccessControlService
from conode.domain.group import GroupId


@dataclass
class DeleteGroupInteractor:
    transaction_manager: TransactionManager
    group_repository: GroupRepository
    company_repository: CompanyRepository
    access_control_service: AccessControlService

    async def execute(self, group_id: GroupId) -> None:
        user = await self.access_control_service.get_authorized_user()

        async with self.transaction_manager:
            group = await self.group_repository.get_by_id(group_id)

            await self.access_control_service.ensure_user_can_manipulate_group(
                user,
                group,
            )

            await self.group_repository.delete(group)
