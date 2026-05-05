from dataclasses import dataclass

from conode.application.interfaces.identity_provider import IdentityProvider
from conode.application.interfaces.repositories import UserRepository
from conode.application.interfaces.transaction_manager import TransactionManager
from conode.application.manage_profile.errors import FailedToUpdateProfileError


@dataclass(frozen=True, slots=True, kw_only=True)
class UpdateProfileRequest:
    first_name: str
    last_name: str
    username: str
    bio: str


@dataclass
class UpdateProfileInteractor:
    user_repository: UserRepository
    identity_provider: IdentityProvider
    transaction_manager: TransactionManager

    async def execute(self, request: UpdateProfileRequest) -> None:
        async with self.transaction_manager:
            user_id = self.identity_provider.get_current_user_id()
            user = await self.user_repository.get_by_id(user_id)
            if user is None:
                raise FailedToUpdateProfileError("User not found", None)

            unique_user = await self.user_repository.get_by_username(
                username=request.username
            )
            if unique_user is not None and unique_user != user:
                raise FailedToUpdateProfileError(
                    "User with that username already exists",
                    [{"key": "username", "value": request.username}],
                )

            user.update_profile(
                first_name=request.first_name,
                last_name=request.last_name,
                username=request.username,
                bio=request.bio,
            )
