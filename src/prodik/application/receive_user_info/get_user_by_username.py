from dataclasses import dataclass

from prodik.application.errors import UserNotFoundError
from prodik.application.interfaces.repositories import UserRepository
from prodik.application.services import AccessControlService
from prodik.domain.user import User, Username


@dataclass
class GetUserByUsernameInteractor:
    access_control_service: AccessControlService
    user_repository: UserRepository

    async def execute(self, username: str) -> User:
        await self.access_control_service.get_authorized_user()

        user = await self.user_repository.get_by_username(Username(username))
        if user is None:
            raise UserNotFoundError("User not found", None)

        return user
