from dataclasses import dataclass

from conode.application.authorization.errors import InvalidCredentialsError
from conode.application.interfaces.identity_provider import IdentityProvider
from conode.application.interfaces.repositories import SessionRepository, UserRepository
from conode.application.interfaces.transaction_manager import TransactionManager
from conode.application.services import AccessService, SessionService


@dataclass(frozen=True, slots=True, kw_only=True)
class RefreshTokenResponse:
    access_token: str
    refresh_token: str
    expires_in: int


@dataclass
class RefreshTokenInteractor:
    identity_provider: IdentityProvider
    session_repository: SessionRepository
    user_repository: UserRepository
    access_service: AccessService
    session_service: SessionService
    transaction_manager: TransactionManager

    async def execute(self, refresh_token: str) -> RefreshTokenResponse:
        async with self.transaction_manager:
            host = self.identity_provider.get_current_ip()
            user_id = self.identity_provider.get_current_user_id()

            user = await self.user_repository.get_by_id(user_id)
            if user is None:
                raise InvalidCredentialsError("Invalid email or password", None)

            session = await self.session_repository.get_by_host(host)
            if session is None:
                raise InvalidCredentialsError("Invalid email or password", None)

            self.access_service.verify_token(session, refresh_token)

            session_service_response = await self.session_service.process(user, host)

            return RefreshTokenResponse(
                access_token=session_service_response.access_token,
                refresh_token=session_service_response.refresh_token,
                expires_in=session_service_response.expires_in,
            )
