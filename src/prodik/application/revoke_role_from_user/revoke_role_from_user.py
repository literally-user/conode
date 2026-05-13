from dataclasses import dataclass

from prodik.application.errors import (
    GrantNotFoundError,
    RoleNotFoundError,
    UserNotFoundError,
)
from prodik.application.interfaces.repositories import (
    RoleRepository,
    UserGrantRepository,
    UserRepository,
)
from prodik.application.interfaces.transaction_manager import TransactionManager
from prodik.application.services import AccessControlService
from prodik.domain.role import RoleId
from prodik.domain.user import UserId


@dataclass
class RevokeRoleFromUserInteractor:
    user_grant_repository: UserGrantRepository
    role_repository: RoleRepository
    user_repository: UserRepository
    access_control_service: AccessControlService
    transaction_manager: TransactionManager

    async def execute(self, user_id: UserId, role_id: RoleId) -> None:
        async with self.transaction_manager:
            executor = await self.access_control_service.get_authorized_user()

            role = await self.role_repository.get_by_id(role_id)
            if role is None:
                raise RoleNotFoundError("Role not found", None)

            await self.access_control_service.ensure_user_can_manipulate_role(
                executor,
                role,
            )

            user = await self.user_repository.get_by_id(user_id)
            if user is None:
                raise UserNotFoundError("User not found", None)

            grant = await self.user_grant_repository.get_by_user_and_role_id(
                user.id, role.id
            )
            if grant is None:
                raise GrantNotFoundError("Grant not found", None)

            await self.user_grant_repository.delete(grant)
