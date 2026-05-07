from dataclasses import dataclass

import structlog

from prodik.application.errors import UserAlreadyExistsError, UserNotFoundError
from prodik.application.interfaces.identity_provider import IdentityProvider
from prodik.application.interfaces.repositories import UserRepository
from prodik.application.interfaces.transaction_manager import TransactionManager
from prodik.domain.user import Email

logger = structlog.get_logger()


@dataclass
class UpdateCurrentUserProfileRequestDTO:
    username: str
    first_name: str
    last_name: str
    email: str
    bio: str


@dataclass
class UpdateCurrentUserProfileInteractor:
    user_repository: UserRepository
    identity_provider: IdentityProvider
    transaction_manager: TransactionManager

    async def execute(self, request: UpdateCurrentUserProfileRequestDTO) -> None:
        async with self.transaction_manager:
            user_meta = self.identity_provider.get_current_user_meta()

            logger.info("Received user meta")

            user = await self.user_repository.get_by_id(user_meta["user_id"])
            if user is None:
                raise UserNotFoundError("User not found", None)

            logger.info("Received user", user_id=user.id)

            unique_user = await self.user_repository.get_by_email(Email(request.email))
            if unique_user is not None and unique_user != user:
                raise UserAlreadyExistsError(
                    "User with this email already exists",
                    [{"key": "email", "value": request.email}],
                )

            logger.info("Email is unique", email=request.email)

            user.update_profile(
                first_name=request.first_name,
                last_name=request.last_name,
                username=request.username,
                email=request.email,
                bio=request.bio,
            )
