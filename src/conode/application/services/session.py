from dataclasses import dataclass
from uuid import uuid7

from conode.application.interfaces.identity_provider import IdentityProvider
from conode.application.interfaces.repositories import SessionRepository
from conode.application.interfaces.token_managers import (
    AccessTokenManager,
    RefreshTokenManager,
)
from conode.application.interfaces.transaction_manager import TransactionManager
from conode.domain.authorization import Session, SessionId
from conode.domain.user import User


@dataclass(frozen=True, slots=True, kw_only=True)
class SessionServiceResponse:
    access_token: str
    refresh_token: str
    expires_in: int


@dataclass
class SessionService:
    identity_provider: IdentityProvider
    session_repository: SessionRepository
    access_token_manager: AccessTokenManager
    refresh_token_manager: RefreshTokenManager
    transaction_manager: TransactionManager

    async def execute(self, user: User, host: str) -> SessionServiceResponse:
        host = self.identity_provider.get_current_ip()
        access_token, expires_in = self.access_token_manager.encode(user)
        refresh_token = self.refresh_token_manager.encode()

        session = await self.session_repository.get_by_host(host)
        if session is not None:
            session.update_token(refresh_token)
            await self.session_repository.update(session)
        else:
            session = Session.new(
                SessionId(uuid7()),
                user,
                host,
                refresh_token,
            )
            await self.session_repository.create(session)

        return SessionServiceResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=expires_in,
        )
