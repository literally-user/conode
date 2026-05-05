from dataclasses import dataclass

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
from conode.application.services import SessionService


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
    session_service: SessionService

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

            session_service_response = await self.session_service.process(user, host)

            return LoginResponseDTO(
                access_token=session_service_response.access_token,
                refresh_token=session_service_response.refresh_token,
                expires_in=session_service_response.expires_in,
            )
