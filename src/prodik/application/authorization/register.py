from dataclasses import dataclass
from uuid import uuid7

import structlog

from prodik.application.authorization.errors import UserAlreadyExistsError
from prodik.application.interfaces.identity_provider import IdentityProvider
from prodik.application.interfaces.repositories import (
    LocalAuhthorizationRepository,
    UserRepository,
)
from prodik.application.interfaces.token_managers import (
    AccessTokenManager,
    RefreshTokenManager,
)
from prodik.application.interfaces.transaction_manager import TransactionManager
from prodik.application.services import SessionService
from prodik.domain.authorization import (
    LocalAuthorization,
    LocalAuthorizationId,
)
from prodik.domain.user import Email, User, UserId, Username

logger = structlog.get_logger()


@dataclass(frozen=True, slots=True, kw_only=True)
class RegisterRequestDTO:
    password: str
    first_name: str
    last_name: str
    username: str
    email: str


@dataclass(frozen=True, slots=True, kw_only=True)
class RegisterResponseDTO:
    access_token: str
    refresh_token: str
    expires_in: int


@dataclass
class RegisterInteractor:
    user_repository: UserRepository
    authorization_repository: LocalAuhthorizationRepository

    transaction_manager: TransactionManager
    access_token_manager: AccessTokenManager
    refresh_token_manager: RefreshTokenManager

    identity_provider: IdentityProvider
    session_service: SessionService

    async def execute(self, request: RegisterRequestDTO) -> RegisterResponseDTO:
        async with self.transaction_manager:
            host = self.identity_provider.get_current_ip()
            user = await self.user_repository.get_by_username_or_email(
                Username(request.username),
                Email(request.email),
            )
            logger.info("3")
            if user is not None:
                raise UserAlreadyExistsError(
                    "User with this username or email already exists",
                    meta=[
                        {"key": "email", "value": request.email},
                        {"key": "username", "value": request.username},
                    ],
                )
            logger.info("Пользователя с таким ником нет")

            user = User.new(
                UserId(uuid7()),
                request.first_name,
                request.last_name,
                request.username,
                request.email,
                "",
            )
            await self.user_repository.create(user)

            authorization = LocalAuthorization.new(
                LocalAuthorizationId(uuid7()), user, request.password
            )
            session_service_response = await self.session_service.process(user, host)

            await self.authorization_repository.create(authorization)
            return RegisterResponseDTO(
                access_token=session_service_response.access_token,
                refresh_token=session_service_response.refresh_token,
                expires_in=session_service_response.expires_in,
            )
