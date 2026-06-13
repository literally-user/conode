from dataclasses import dataclass

from prodik.application.interfaces.repositories import RoleRepository
from prodik.application.interfaces.transaction_manager import TransactionManager
from prodik.application.services import AccessControlService
from prodik.domain.role import RoleId


@dataclass
class DeleteRoleInteractor:
    role_repository: RoleRepository
    transaction_manager: TransactionManager
    access_control_service: AccessControlService

    async def execute(self, role_id: RoleId) -> None:
        async with self.transaction_manager:
            user = await self.access_control_service.get_authorized_user()

            role = await self.role_repository.get_by_id(role_id)

            await self.access_control_service.ensure_user_can_manipulate_role(
                user,
                role,
            )

            await self.role_repository.delete(role)
