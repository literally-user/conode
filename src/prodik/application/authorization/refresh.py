from dataclasses import dataclass

from prodik.application.errors import SessionNotFoundError
from prodik.application.interfaces.identity_provider import IdentityProvider
from prodik.application.interfaces.repositories import SessionRepository, UserRepository
from prodik.application.interfaces.token_managers import (
    AccessTokenManager,
    RefreshTokenManager,
)
from prodik.application.interfaces.transaction_manager import TransactionManager


@dataclass(slots=True, frozen=True, kw_only=True)
class RefreshTokenResponse:
    access_token: str
    refresh_token: str
    expires_in: int


@dataclass
class RefreshTokenInteractor:
    user_repository: UserRepository
    identity_provider: IdentityProvider
    session_repository: SessionRepository
    access_token_manager: AccessTokenManager
    refresh_token_manager: RefreshTokenManager
    transaction_manager: TransactionManager

    async def execute(self, token: str) -> RefreshTokenResponse:
        async with self.transaction_manager:
            user_meta = self.identity_provider.get_current_user_meta()

            user = await self.user_repository.get_by_id(user_meta["user_id"])
            if user is None:
                raise SessionNotFoundError("User not found", None)

            session = await self.session_repository.get_by_token(token)
            if session is None:
                raise SessionNotFoundError("Session not found", None)

            access_token, expires_in = self.access_token_manager.encode(user)
            refresh_token = self.refresh_token_manager.encode()

            session.update_token(refresh_token)

            await self.session_repository.update(session)

            return RefreshTokenResponse(
                access_token=access_token,
                refresh_token=refresh_token,
                expires_in=expires_in,
            )
