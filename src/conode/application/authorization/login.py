from dataclasses import dataclass
from uuid import uuid7

from conode.application.authorization.errors import InvalidCredentialsError
from conode.application.interfaces.identity_provider import IdentityProvider
from conode.application.interfaces.password_hasher import PasswordHasher
from conode.application.interfaces.repositories import (
    LocalAuhthorizationRepository,
    SessionRepository,
    UserRepository,
)
from conode.application.interfaces.token_managers import (
    AccessTokenManager,
    RefreshTokenManager,
)
from conode.application.interfaces.transaction_manager import TransactionManager
from conode.domain.authorization import Session, SessionId


@dataclass(frozen=True, slots=True, kw_only=True)
class LoginRequestDTO:
    password: str
    email: str


@dataclass(frozen=True, slots=True, kw_only=True)
class LoginResponseDTO:
    access_token: str
    refresh_token: str
    expires_in: int


@dataclass
class LoginInteractor:
    identity_provider: IdentityProvider
    password_hasher: PasswordHasher
    authorization_repository: LocalAuhthorizationRepository
    session_repository: SessionRepository
    user_repository: UserRepository
    access_token_manager: AccessTokenManager
    refresh_token_manager: RefreshTokenManager
    transaction_manager: TransactionManager

    async def execute(self, request: LoginRequestDTO) -> LoginResponseDTO:
        async with self.transaction_manager:
            host = self.identity_provider.get_current_ip()
            user = await self.user_repository.get_by_email(request.email)
            if user is None:
                raise InvalidCredentialsError(
                    "Invalid email or password",
                    [
                        {"key": "email", "value": request.email},
                        {"key": "password", "value": request.password},
                    ],
                )

            authorization = await self.authorization_repository.get_by_user_id(user.id)
            if authorization is None:
                raise InvalidCredentialsError(
                    "Invalid email or password",
                    [
                        {"key": "email", "value": request.email},
                        {"key": "password", "value": request.password},
                    ],
                )

            if not self.password_hasher.verify(
                authorization.password,
                request.password,
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
            if session is not None:
                session.update_token(refresh_token)
                await self.session_repository.update(session)
            else:
                session = Session.new(
                    SessionId(uuid7()),
                    user,
                    host,
                    refresh_token,
                )
                await self.session_repository.create(session)

            return LoginResponseDTO(
                access_token=access_token,
                refresh_token=refresh_token,
                expires_in=expires_in,
            )
