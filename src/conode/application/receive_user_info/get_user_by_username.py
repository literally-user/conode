from dataclasses import dataclass

from conode.application.errors import UserNotFoundError
from conode.application.interfaces.repositories import UserRepository
from conode.application.services import AuthorizationService
from conode.domain.user import User, Username


@dataclass
class GetUserByUsernameInteractor:
    authorization_service: AuthorizationService
    user_repository: UserRepository

    async def execute(self, username: str) -> User:
        await self.authorization_service.get_authorized_user()

        user = await self.user_repository.get_by_username(Username(username))
        if user is None:
            raise UserNotFoundError(
                "User not found",
                [{"key": "username", "value": username}],
            )

        return user
