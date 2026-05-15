from dataclasses import dataclass
from uuid import uuid4

from prodik.application.errors import (
    AuthorizationNotFoundError,
    InvalidCredentialsError,
    UserNotFoundError,
)
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
from prodik.domain.authorization import Session, SessionId
from prodik.domain.user import Email


@dataclass(frozen=True, slots=True, kw_only=True)
class LoginRequestDTO:
    email: str
    password: str


@dataclass(frozen=True, slots=True, kw_only=True)
class LoginResponseDTO:
    access_token: str
    refresh_token: str
    expires_in: int


@dataclass
class LoginInteractor:
    user_repository: UserRepository
    session_repository: SessionRepository
    authorization_repository: LocalAuthorizationRepository
    password_hasher: PasswordHasher
    identity_provider: IdentityProvider
    transaction_manager: TransactionManager
    access_token_manager: AccessTokenManager
    refresh_token_manager: RefreshTokenManager

    async def execute(self, request: LoginRequestDTO) -> LoginResponseDTO:
        async with self.transaction_manager:
            host = self.identity_provider.get_current_ip()

            user = await self.user_repository.get_by_email(Email(request.email))
            if user is None:
                raise UserNotFoundError(
                    "User not found", [{"key": "email", "value": request.email}]
                )

            authorization = await self.authorization_repository.get_by_user_id(user.id)
            if authorization is None:
                raise AuthorizationNotFoundError(
                    "Authorization not found",
                    [{"key": "user_id", "value": user.id}],
                )

            if not self.password_hasher.verify(
                authorization.password, request.password
            ):
                raise InvalidCredentialsError(
                    "Invalid email or password",
                    [
                        {"key": "email", "value": request.email},
                        {"key": "password", "value": request.password},
                    ],
                )

            access_token, expires_in = self.access_token_manager.encode(user)
            refresh_token = self.refresh_token_manager.encode()

            session = await self.session_repository.get_by_host(host)
            if session is None:
                session = Session.new(
                    id=SessionId(uuid4()), user=user, host=host, token=refresh_token
                )
                await self.session_repository.create(session)
            else:
                session.update_token(refresh_token)

            return LoginResponseDTO(
                access_token=access_token,
                refresh_token=refresh_token,
                expires_in=expires_in,
            )
