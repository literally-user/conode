from dataclasses import dataclass

from prodik.application.errors import (
    GrantNotFoundError,
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

            await self.access_control_service.ensure_user_can_manipulate_role(
                executor,
                role,
            )

            if executor.id == user_id:
                user = executor
            else:
                user = await self.user_repository.get_by_id(user_id)

            grant = await self.user_grant_repository.get_by_user_and_role_id(
                user.id,
                role.id,
            )
            if grant is None:
                raise GrantNotFoundError(
                    "Grant by user and role id not found",
                    [
                        {"key": "user_id", "value": user_id},
                        {"key": "role_id", "value": role_id},
                    ],
                )

            await self.user_grant_repository.delete(grant)
