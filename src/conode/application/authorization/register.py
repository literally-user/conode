from dataclasses import dataclass
from uuid import uuid7

from conode.application.authorization.errors import UserAlreadyExistsError
from conode.application.interfaces.identity_provider import IdentityProvider
from conode.application.interfaces.repositories import UserRepository
from conode.application.interfaces.repositories.authorization import (
    LocalAuhthorizationRepository,
    SessionRepository,
)
from conode.application.interfaces.token_managers import (
    AccessTokenManager,
    RefreshTokenManager,
)
from conode.application.interfaces.transaction_manager import TransactionManager
from conode.domain.authorization import (
    LocalAuthorization,
    LocalAuthorizationId,
    Session,
    SessionId,
)
from conode.domain.user import User, UserId


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
    session_repository: SessionRepository

    transaction_manager: TransactionManager
    access_token_manager: AccessTokenManager
    refresh_token_manager: RefreshTokenManager

    identity_provider: IdentityProvider

    async def execute(self, request: RegisterRequestDTO) -> RegisterResponseDTO:
        ip = self.identity_provider.get_current_ip()
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
        )
        authorization = LocalAuthorization.new(
            LocalAuthorizationId(uuid7()), user, request.password
        )

        access_token, expires_in = self.access_token_manager.encode(user)
        refresh_token = self.refresh_token_manager.encode()
        session = Session.new(
            SessionId(uuid7()),
            user,
            refresh_token,
            ip,
        )

        async with self.transaction_manager:
            await self.user_repository.create(user)
            await self.authorization_repository.create(authorization)
            await self.session_repository.create(session)

        return RegisterResponseDTO(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=expires_in,
        )
