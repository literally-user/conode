from dataclasses import dataclass

from prodik.application.errors import (
    CompanyNotFoundError,
    GroupNotFoundError,
)
from prodik.application.interfaces.repositories import (
    CompanyRepository,
    GroupRepository,
)
from prodik.application.interfaces.transaction_manager import TransactionManager
from prodik.application.services import AccessControlService
from prodik.domain.group import GroupId


@dataclass
class DeleteGroupInteractor:
    transaction_manager: TransactionManager
    group_repository: GroupRepository
    company_repository: CompanyRepository
    access_control_service: AccessControlService

    async def execute(self, group_id: GroupId) -> None:
        async with self.transaction_manager:
            user = await self.access_control_service.get_authorized_user()

            group = await self.group_repository.get_by_id(group_id)
            if group is None:
                raise GroupNotFoundError("Group not found", None)

            company = await self.company_repository.get_by_id(group.company_id)
            if company is None:
                raise CompanyNotFoundError("Company not found", None)

            await self.access_control_service.ensure_user_can_manipulate_group(
                user,
                group,
            )

            await self.group_repository.delete(group)
