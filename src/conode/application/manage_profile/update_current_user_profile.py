from dataclasses import dataclass

from conode.application.interfaces.repositories import UserRepository
from conode.application.interfaces.transaction_manager import TransactionManager
from conode.application.services import AccessControlService


@dataclass
class UpdateCurrentUserProfileRequestDTO:
    username: str
    first_name: str
    last_name: str
    bio: str


@dataclass
class UpdateCurrentUserProfileInteractor:
    user_repository: UserRepository
    transaction_manager: TransactionManager
    access_control_service: AccessControlService

    async def execute(self, request: UpdateCurrentUserProfileRequestDTO) -> None:
        user = await self.access_control_service.get_authorized_user()

        async with self.transaction_manager:
            user.update_profile(
                first_name=request.first_name,
                last_name=request.last_name,
                username=request.username,
                bio=request.bio,
            )

            await self.user_repository.update(user)
