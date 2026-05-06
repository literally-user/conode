from dataclasses import dataclass

from prodik.application.authorization.errors import (
    InvalidCredentialsError,
    UserAlreadyExistsError,
)
from prodik.application.interfaces.identity_provider import IdentityProvider
from prodik.application.interfaces.repositories import SessionRepository, UserRepository
from prodik.application.interfaces.transaction_manager import TransactionManager
from prodik.application.services import AccessService
from prodik.domain.user import Username


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
    session_repository: SessionRepository
    transaction_manager: TransactionManager
    access_service: AccessService

    async def execute(self, request: UpdateProfileRequest) -> None:
        async with self.transaction_manager:
            host = self.identity_provider.get_current_ip()
            user_id = self.identity_provider.get_current_user_id()

            user = await self.user_repository.get_by_id(user_id)
            if user is None:
                raise InvalidCredentialsError("User not found", None)

            session = await self.session_repository.get_by_host(host)
            if session is None:
                raise InvalidCredentialsError("Session not found", None)

            self.access_service.ensure_session_active(session, user)

            unique_user = await self.user_repository.get_by_username(
                username=Username(request.username)
            )
            if unique_user is not None and unique_user != user:
                raise UserAlreadyExistsError(
                    "User with that username already exists",
                    [{"key": "username", "value": request.username}],
                )

            user.update_profile(
                first_name=request.first_name,
                last_name=request.last_name,
                username=request.username,
                bio=request.bio,
            )
