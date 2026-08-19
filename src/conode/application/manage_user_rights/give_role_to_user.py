from dataclasses import dataclass
from uuid import uuid4

from conode.application.errors import (
    GrantAlreadyExistsError,
)
from conode.application.interfaces.repositories import (
    RoleRepository,
    UserGrantRepository,
    UserRepository,
)
from conode.application.interfaces.transaction_manager import TransactionManager
from conode.application.services import AccessControlService, AuthorizationService
from conode.domain.grant import UserGrant, UserGrantId
from conode.domain.role import RoleId
from conode.domain.user import UserId


@dataclass
class GiveRoleToUserInteractor:
    access_control_service: AccessControlService
    authorization_service: AuthorizationService
    user_repository: UserRepository
    user_grant_repository: UserGrantRepository
    transaction_manager: TransactionManager
    role_repository: RoleRepository

    async def execute(self, user_id: UserId, role_id: RoleId) -> UserGrant:
        async with self.transaction_manager:
            executor = await self.authorization_service.get_authorized_user()

            role = await self.role_repository.get_by_id(role_id)
            user = await self.user_repository.get_by_id(user_id)

            await self.access_control_service.ensure_user_can_manipulate_role(
                executor,
                role,
            )

            grant = await self.user_grant_repository.get_by_user_and_role_id(
                user.id,
                role.id,
            )
            if grant is not None:
                raise GrantAlreadyExistsError(
                    "Grant already exists",
                    [
                        {"key": "user_id", "value": user.id},
                        {"key": "role_id", "value": role.id},
                    ],
                )

            grant = UserGrant.new(
                user_grant_id=UserGrantId(uuid4()),
                role=role,
                user=user,
            )

            await self.user_grant_repository.create(grant)

            return grant
