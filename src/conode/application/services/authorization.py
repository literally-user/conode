from dataclasses import dataclass
from typing import NamedTuple
from uuid import uuid4

from conode.application.interfaces.password_hasher import PasswordHasher
from conode.application.interfaces.token_managers import (
    AccessTokenManager,
    RefreshTokenManager,
)
from conode.domain.auth import Authorization, AuthorizationId, Session, SessionId
from conode.domain.user import User


class AuthorizationServiceResponse(NamedTuple):
    session: Session
    authorization: Authorization
    expires_in: int
    refresh_token: str


@dataclass
class AuthorizationService:
    access_token_manager: AccessTokenManager
    refresh_token_manager: RefreshTokenManager
    password_hasher: PasswordHasher

    def generate_authorization_stuff(
        self, user: User, password: str, ip: str
    ) -> AuthorizationServiceResponse:
        access_token, expires_in = self.access_token_manager.encode(user)
        refresh_token = self.refresh_token_manager.encode()
        hashed_password = self.password_hasher.hash(password)

        session = Session.new(SessionId(uuid4()), refresh_token, access_token, user, ip)
        authorization = Authorization.new(
            AuthorizationId(uuid4()), hashed_password, user
        )

        return AuthorizationServiceResponse(
            session=session,
            authorization=authorization,
            expires_in=expires_in,
            refresh_token=refresh_token,
        )
