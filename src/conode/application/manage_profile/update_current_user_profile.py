from dataclasses import dataclass

from conode.application.interfaces.repositories import UserRepository
from conode.application.interfaces.transaction_manager import TransactionManager
from conode.application.services import AuthorizationService


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
    authorization_service: AuthorizationService

    async def execute(self, request: UpdateCurrentUserProfileRequestDTO) -> None:
        async with self.transaction_manager:
            user = await self.authorization_service.get_authorized_user()
            user.update_profile(
                first_name=request.first_name,
                last_name=request.last_name,
                username=request.username,
                bio=request.bio,
            )

            await self.user_repository.update(user)
