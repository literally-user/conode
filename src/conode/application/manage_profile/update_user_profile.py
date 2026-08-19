from dataclasses import dataclass

from conode.application.interfaces.repositories import UserRepository
from conode.application.interfaces.transaction_manager import TransactionManager
from conode.application.services import AccessControlService, AuthorizationService
from conode.domain.user import UserId


@dataclass(frozen=True, slots=True, kw_only=True)
class UpdateUserProfileRequestDTO:
    first_name: str
    last_name: str
    username: str
    bio: str


@dataclass
class UpdateUserProfileInteractor:
    access_control_service: AccessControlService
    authorization_service: AuthorizationService
    transaction_manager: TransactionManager
    user_repository: UserRepository

    async def execute(
        self, user_id: UserId, request: UpdateUserProfileRequestDTO
    ) -> None:
        async with self.transaction_manager:
            user = await self.authorization_service.get_authorized_user()
            if user.id == user_id:
                target = user
            else:
                self.access_control_service.ensure_user_can_manipulate_user_profiles(
                    user
                )
                target = await self.user_repository.get_by_id(user_id)

            target.update_profile(
                username=request.username,
                first_name=request.first_name,
                last_name=request.last_name,
                bio=request.bio,
            )

            await self.user_repository.update(target)
