from dataclasses import dataclass

from prodik.application.errors import (
    CompanyNotFoundError,
    GroupNotFoundError,
    NotEnoughRightsError,
)
from prodik.application.interfaces.identity_provider import IdentityProvider
from prodik.application.interfaces.repositories import (
    CompanyRepository,
    GroupRepository,
    UserRepository,
)
from prodik.application.interfaces.transaction_manager import TransactionManager
from prodik.application.services import AccessControlService
from prodik.domain.group import GroupId


@dataclass
class DeleteGroupInteractor:
    identity_provider: IdentityProvider
    transaction_manager: TransactionManager
    group_repository: GroupRepository
    user_repository: UserRepository
    company_repository: CompanyRepository
    access_control_service: AccessControlService

    async def execute(self, group_id: GroupId) -> None:
        async with self.transaction_manager:
            user = await self.access_control_service.get_authorized_user()

            company = await self.company_repository.get_by_user_id(user.id)
            if company is None:
                raise CompanyNotFoundError("Company not found", None)

            group = await self.group_repository.get_by_id(group_id)
            if group is None:
                raise GroupNotFoundError("Group not found", None)

            if group.company_id != company.id and not user.is_admin():
                raise NotEnoughRightsError(
                    "Not enough rights to perform operation", None
                )

            await self.group_repository.delete(group)
