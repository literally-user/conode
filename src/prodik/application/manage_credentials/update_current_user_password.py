from dataclasses import dataclass

import structlog

from prodik.application.errors import (
    AuthorizationNotFoundError,
    InvalidOldPasswordError,
    SessionNotFoundError,
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
from prodik.application.services import AccessControlService


@dataclass(frozen=True, slots=True, kw_only=True)
class UpdateCurrentUserPasswordRequestDTO:
    old_password: str
    new_password: str


@dataclass(frozen=True, slots=True, kw_only=True)
class UpdateCurrentUserPasswordResponseDTO:
    access_token: str
    refresh_token: str
    expires_in: int


logger = structlog.get_logger()


@dataclass
class UpdateCurrentUserPasswordInteractor:
    user_repository: UserRepository
    session_repository: SessionRepository
    local_authorization_repository: LocalAuthorizationRepository
    transaction_manager: TransactionManager
    identity_provider: IdentityProvider
    password_hasher: PasswordHasher
    access_token_manager: AccessTokenManager
    refresh_token_manager: RefreshTokenManager
    access_control_service: AccessControlService

    async def execute(
        self, request: UpdateCurrentUserPasswordRequestDTO
    ) -> UpdateCurrentUserPasswordResponseDTO:
        async with self.transaction_manager:
            host = self.identity_provider.get_current_ip()
            user = await self.access_control_service.get_authorized_user()

            authorization = await self.local_authorization_repository.get_by_user_id(
                user.id
            )
            if authorization is None:
                raise AuthorizationNotFoundError("Authorization not found", None)

            if not self.password_hasher.verify(
                authorization.password, request.old_password
            ):
                raise InvalidOldPasswordError(
                    "Invalid old password",
                    [
                        {"key": "old_password", "value": request.old_password},
                    ],
                )

            hashed_password = self.password_hasher.hash(request.new_password)
            authorization.update_password(hashed_password)
            user.increment_revision()

            session = await self.session_repository.get_by_host(host)
            if session is None:
                raise SessionNotFoundError("Session not found", None)

            access_token, expires_in = self.access_token_manager.encode(user)
            refresh_token = self.refresh_token_manager.encode()

            session.update_token(refresh_token)

            await self.user_repository.update(user)
            await self.local_authorization_repository.update(authorization)
            await self.session_repository.update(session)

            return UpdateCurrentUserPasswordResponseDTO(
                access_token=access_token,
                refresh_token=refresh_token,
                expires_in=expires_in,
            )
