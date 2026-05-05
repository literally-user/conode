from dataclasses import dataclass
from uuid import uuid7

from conode.application.authorization.errors import UserAlreadyExistsError
from conode.application.interfaces.identity_provider import IdentityProvider
from conode.application.interfaces.repositories import (
    LocalAuhthorizationRepository,
    UserRepository,
)
from conode.application.interfaces.token_managers import (
    AccessTokenManager,
    RefreshTokenManager,
)
from conode.application.interfaces.transaction_manager import TransactionManager
from conode.application.services import SessionService
from conode.domain.authorization import (
    LocalAuthorization,
    LocalAuthorizationId,
)
from conode.domain.user import User, UserId


@dataclass(frozen=True, slots=True, kw_only=True)
class RegisterRequestDTO:
    password: str
    first_name: str
    last_name: str
    username: str
    email: str
    bio: str


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
                request.username,
                request.email,
            )
            if user is not None:
                raise UserAlreadyExistsError(
                    "User with this username or email already exists",
                    meta=[
                        {"key": "email", "value": request.email},
                        {"key": "username", "value": request.username},
                    ],
                )

            user = User.new(
                UserId(uuid7()),
                request.first_name,
                request.last_name,
                request.username,
                request.email,
                request.bio,
            )
            authorization = LocalAuthorization.new(
                LocalAuthorizationId(uuid7()), user, request.password
            )
            session_service_response = await self.session_service.process(user, host)

            await self.user_repository.create(user)
            await self.authorization_repository.create(authorization)

            return RegisterResponseDTO(
                access_token=session_service_response.access_token,
                refresh_token=session_service_response.refresh_token,
                expires_in=session_service_response.expires_in,
            )
