from dataclasses import dataclass

from prodik.application.interfaces.identity_provider import IdentityProvider
from prodik.application.interfaces.password_hasher import PasswordHasher
from prodik.application.interfaces.repositories import (
    LocalAuhthorizationRepository,
    SessionRepository,
    UserRepository,
)
from prodik.application.interfaces.transaction_manager import TransactionManager
from prodik.application.manage_password.errors import FailedToUpdatePasswordError
from prodik.application.services import AccessService, SessionService


@dataclass(frozen=True, slots=True, kw_only=True)
class UpdatePasswordRequest:
    old_password: str
    new_password: str


@dataclass(frozen=True, slots=True, kw_only=True)
class UpdatePasswordResponse:
    access_token: str
    refresh_token: str
    expires_in: int


@dataclass
class UpdatePasswordInteractor:
    authorization_repository: LocalAuhthorizationRepository
    transaction_manager: TransactionManager
    session_repository: SessionRepository
    identity_provider: IdentityProvider
    user_repository: UserRepository
    password_hasher: PasswordHasher
    session_service: SessionService
    access_service: AccessService

    async def execute(self, request: UpdatePasswordRequest) -> UpdatePasswordResponse:
        async with self.transaction_manager:
            host = self.identity_provider.get_current_ip()
            user_id = self.identity_provider.get_current_user_id()

            session = await self.session_repository.get_by_host(host)
            if session is None:
                raise FailedToUpdatePasswordError("Session not found", None)

            user = await self.user_repository.get_by_id(user_id)
            if user is None:
                raise FailedToUpdatePasswordError("User not found", None)

            self.access_service.ensure_session_active(session, user)

            authorization = await self.authorization_repository.get_by_user_id(user_id)
            if authorization is None:
                raise FailedToUpdatePasswordError("Authorization not found", None)
            if not self.password_hasher.verify(
                authorization.password, request.old_password
            ):
                raise FailedToUpdatePasswordError(
                    "Invalid old password",
                    [{"key": "old_password", "value": request.old_password}],
                )

            user.increment_revision()

            hashed_password = self.password_hasher.hash(request.new_password)
            authorization.update_password(hashed_password)

            await self.user_repository.update(user)
            await self.authorization_repository.update(authorization)

            session_service_response = await self.session_service.process(user, host)

            return UpdatePasswordResponse(
                access_token=session_service_response.access_token,
                refresh_token=session_service_response.refresh_token,
                expires_in=session_service_response.expires_in,
            )
