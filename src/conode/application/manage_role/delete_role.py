from dataclasses import dataclass

from conode.application.interfaces.repositories import RoleRepository
from conode.application.interfaces.transaction_manager import TransactionManager
from conode.application.services import AccessControlService
from conode.domain.role import RoleId


@dataclass
class DeleteRoleInteractor:
    role_repository: RoleRepository
    transaction_manager: TransactionManager
    access_control_service: AccessControlService

    async def execute(self, role_id: RoleId) -> None:
        user = await self.access_control_service.get_authorized_user()

        async with self.transaction_manager:
            role = await self.role_repository.get_by_id(role_id)

            await self.access_control_service.ensure_user_can_manipulate_role(
                user,
                role,
            )

            await self.role_repository.delete(role)
