from dataclasses import dataclass

from conode.application.auth.shared import AuthorizedResponseDTO
from conode.application.interfaces.identity_provider import IdentityProvider
from conode.application.interfaces.repositories import SessionRepository
from conode.application.interfaces.token_managers import (
    AccessTokenManager,
    RefreshTokenManager,
)
from conode.application.interfaces.transaction_manager import TransactionManager
from conode.application.services import AccessControlService, AuthorizationService


@dataclass
class RefreshTokenInteractor:
    identity_provider: IdentityProvider
    session_repository: SessionRepository
    transaction_manager: TransactionManager
    refresh_token_manager: RefreshTokenManager
    access_token_manager: AccessTokenManager
    access_control_service: AccessControlService
    authorization_service: AuthorizationService

    async def execute(self) -> AuthorizedResponseDTO:
        async with self.transaction_manager:
            current_refresh_token = self.identity_provider.get_current_refresh_token()

            user = await self.access_control_service.get_authorized_user()
            session = await self.session_repository.get_by_refresh_token(
                current_refresh_token
            )

            access_token, expires_in = self.access_token_manager.encode(user)
            refresh_token = self.refresh_token_manager.encode()

            session.set_access_token(access_token)
            session.set_refresh_token(refresh_token)

            await self.session_repository.update(session)

            return AuthorizedResponseDTO(
                access_token=access_token,
                refresh_token=refresh_token,
                expires_in=expires_in,
            )
