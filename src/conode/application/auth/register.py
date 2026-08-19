from dataclasses import dataclass
from uuid import uuid4

from conode.application.auth.shared import AuthorizedResponseDTO
from conode.application.errors import UserAlreadyExistsError
from conode.application.interfaces.identity_provider import IdentityProvider
from conode.application.interfaces.repositories import (
    AuthorizationRepository,
    SessionRepository,
    UserRepository,
)
from conode.application.interfaces.transaction_manager import TransactionManager
from conode.application.services import AuthorizationService
from conode.domain.user import Email, User, UserId, Username


@dataclass(frozen=True, slots=True, kw_only=True)
class RegisterRequestDTO:
    username: str
    password: str
    first_name: str
    last_name: str
    email: str
    bio: str


@dataclass
class RegisterInteractor:
    user_repository: UserRepository
    identity_provider: IdentityProvider
    session_repository: SessionRepository
    transaction_manager: TransactionManager
    authorization_service: AuthorizationService
    authorization_repository: AuthorizationRepository

    async def execute(self, request: RegisterRequestDTO) -> AuthorizedResponseDTO:
        async with self.transaction_manager:
            user = await self.user_repository.get_by_username_or_email(
                Username(request.username),
                Email(request.email),
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
                UserId(uuid4()),
                username=request.username,
                email=request.email,
                last_name=request.last_name,
                first_name=request.first_name,
                bio=request.bio,
            )

            current_user_ip = self.identity_provider.get_current_ip()

            authorization_service_response = (
                self.authorization_service.generate_authorization_stuff(
                    user,
                    request.password,
                    current_user_ip,
                )
            )

            await self.user_repository.create(user)
            await self.authorization_repository.create(
                authorization_service_response.authorization
            )
            await self.session_repository.create(authorization_service_response.session)

            return AuthorizedResponseDTO(
                access_token=authorization_service_response.session.access_token,
                refresh_token=authorization_service_response.refresh_token,
                expires_in=authorization_service_response.expires_in,
            )
