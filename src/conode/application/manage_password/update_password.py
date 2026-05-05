from dataclasses import dataclass

from conode.application.interfaces.identity_provider import IdentityProvider
from conode.application.interfaces.password_hasher import PasswordHasher
from conode.application.interfaces.repositories import (
    LocalAuhthorizationRepository,
    UserRepository,
)
from conode.application.interfaces.transaction_manager import TransactionManager
from conode.application.manage_password.errors import FailedToUpdatePasswordError
from conode.application.services import SessionService


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
    transaction_manager: TransactionManager
    authorization_repository: LocalAuhthorizationRepository
    identity_provider: IdentityProvider
    user_repository: UserRepository
    password_hasher: PasswordHasher
    session_service: SessionService

    async def execute(self, request: UpdatePasswordRequest) -> UpdatePasswordResponse:
        host = self.identity_provider.get_current_ip()
        user_id = self.identity_provider.get_current_user_id()
        user = await self.user_repository.get_by_id(user_id)
        if user is None:
            raise FailedToUpdatePasswordError("User not found", None)

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
