from dataclasses import dataclass

from conode.application.auth.shared import AuthorizedResponseDTO
from conode.application.interfaces.identity_provider import IdentityProvider
from conode.application.interfaces.repositories import SessionRepository, UserRepository
from conode.application.interfaces.token_managers import (
    AccessTokenManager,
    RefreshTokenManager,
)
from conode.application.interfaces.transaction_manager import TransactionManager
from conode.application.services import AuthorizationService


@dataclass
class RefreshTokenInteractor:
    identity_provider: IdentityProvider
    session_repository: SessionRepository
    transaction_manager: TransactionManager
    refresh_token_manager: RefreshTokenManager
    access_token_manager: AccessTokenManager
    authorization_service: AuthorizationService
    user_repository: UserRepository

    async def execute(self, refresh_token: str) -> AuthorizedResponseDTO:
        async with self.transaction_manager:
            session = await self.session_repository.get_by_refresh_token(refresh_token)
            user = await self.user_repository.get_by_id(session.user_id)

            access_token, expires_in = self.access_token_manager.encode(user)
            new_refresh_token = self.refresh_token_manager.encode()

            session.set_refresh_token(new_refresh_token)

            await self.session_repository.update(session)

            return AuthorizedResponseDTO(
                access_token=access_token,
                refresh_token=new_refresh_token,
                expires_in=expires_in,
            )
