from dataclasses import dataclass
from uuid import uuid4

import structlog

from prodik.application.errors import UserAlreadyExistsError
from prodik.application.interfaces.identity_provider import IdentityProvider
from prodik.application.interfaces.password_hasher import PasswordHasher
from prodik.application.interfaces.repositories import (
    LocalAuthorizationRepository,
    SessionRepository,
    UserRepository,
)
from prodik.application.interfaces.token_managers import (
    AccessTokenManager,
    RefreshTokenManager,
)
from prodik.application.interfaces.transaction_manager import TransactionManager
from prodik.domain.authorization import (
    LocalAuthorization,
    LocalAuthorizationId,
    Session,
    SessionId,
)
from prodik.domain.user import Email, User, UserId, Username

logger = structlog.get_logger()


@dataclass(frozen=True, slots=True, kw_only=True)
class RegisterRequestDTO:
    first_name: str
    last_name: str
    username: str
    password: str
    email: str


@dataclass(frozen=True, slots=True, kw_only=True)
class RegisterResponseDTO:
    access_token: str
    refresh_token: str
    expires_in: int


@dataclass
class RegisterInteractor:
    user_repository: UserRepository
    session_repository: SessionRepository
    authorization_repository: LocalAuthorizationRepository
    access_token_manager: AccessTokenManager
    refresh_token_manager: RefreshTokenManager
    transaction_manager: TransactionManager
    identity_provider: IdentityProvider
    password_hasher: PasswordHasher

    async def execute(self, request: RegisterRequestDTO) -> RegisterResponseDTO:
        async with self.transaction_manager:
            host = self.identity_provider.get_current_ip()
            user = await self.user_repository.get_by_username_or_email(
                username=Username(request.username),
                email=Email(request.email),
            )
            if user is not None:
                raise UserAlreadyExistsError(
                    "User with this username or email already exists",
                    [
                        {"key": "email", "value": request.email},
                        {"key": "username", "value": request.username},
                    ],
                )

            user = User.new(
                id=UserId(uuid4()),
                first_name=request.first_name,
                last_name=request.last_name,
                username=request.username,
                email=request.email,
                bio="",
            )

            access_token, expires_in = self.access_token_manager.encode(user)
            refresh_token = self.refresh_token_manager.encode()

            session = Session.new(
                id=SessionId(uuid4()),
                user=user,
                host=host,
                token=refresh_token,
            )

            hashed_password = self.password_hasher.hash(request.password)

            authorization = LocalAuthorization.new(
                id=LocalAuthorizationId(uuid4()), user=user, password=hashed_password
            )

            await self.user_repository.create(user=user)
            await self.session_repository.create(session=session)
            await self.authorization_repository.create(authorization=authorization)

            return RegisterResponseDTO(
                access_token=access_token,
                refresh_token=refresh_token,
                expires_in=expires_in,
            )
