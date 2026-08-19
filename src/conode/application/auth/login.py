from dataclasses import dataclass

from conode.application.auth.shared import AuthorizedResponseDTO
from conode.application.errors import InvalidCredentialsError, UserNotFoundError
from conode.application.interfaces.identity_provider import IdentityProvider
from conode.application.interfaces.password_hasher import PasswordHasher
from conode.application.interfaces.repositories import (
    AuthorizationRepository,
    SessionRepository,
    UserRepository,
)
from conode.application.interfaces.transaction_manager import TransactionManager
from conode.application.services import AuthorizationService
from conode.domain.user import Email


@dataclass(frozen=True, slots=True, kw_only=True)
class LoginRequestDTO:
    email: str
    password: str


@dataclass
class LoginInteractor:
    user_repository: UserRepository
    identity_provider: IdentityProvider
    authorization_repository: AuthorizationRepository
    authorization_service: AuthorizationService
    session_repository: SessionRepository
    transaction_manager: TransactionManager
    password_hasher: PasswordHasher

    async def execute(self, request: LoginRequestDTO) -> AuthorizedResponseDTO:
        async with self.transaction_manager:
            user = await self.user_repository.get_by_email(Email(request.email))
            if user is None:
                raise UserNotFoundError(
                    "User with this email not found",
                    meta=[{"key": "email", "value": request.email}],
                )

            authorization = await self.authorization_repository.get_by_user(user)

            if not self.password_hasher.verify(
                authorization.hashed_password, request.password
            ):
                raise InvalidCredentialsError(
                    "Passwords doesn't match",
                    meta=[{"key": "password", "value": request.password}],
                )

            current_user_ip = self.identity_provider.get_current_ip()

            authorization_service_response = (
                self.authorization_service.generate_authorization_stuff(
                    user,
                    request.password,
                    current_user_ip,
                )
            )
            await self.session_repository.upsert(authorization_service_response.session)

            return AuthorizedResponseDTO(
                access_token=authorization_service_response.access_token,
                refresh_token=authorization_service_response.refresh_token,
                expires_in=authorization_service_response.expires_in,
            )
