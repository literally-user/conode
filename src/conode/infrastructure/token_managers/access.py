from datetime import UTC, datetime, timedelta

import jwt

from conode.application.interfaces.token_managers import (
    AccessTokenManager,
    AccessTokenManagerResponse,
    UserMeta,
)
from conode.domain.user.model import User, UserSystemRole
from conode.infrastructure.config import SecretsConfig


class AccessTokenManagerImpl(AccessTokenManager):
    def __init__(self, config: SecretsConfig) -> None:
        self.config = config

    def encode(self, user: User) -> AccessTokenManagerResponse:
        now = datetime.now(UTC)
        token = jwt.encode(
            {
                "sub": str(user.id),
                "email": str(user.email.value),
                "role": str(user.system_role),
                "iss": self.config.issuer,
                "aud": self.config.audience,
                "exp": now + timedelta(seconds=self.config.expires_in),
            },
            self.config.private_key,
            algorithm="RS256",
        )
        return AccessTokenManagerResponse(
            expires_in=self.config.expires_in,
            token=token,
        )

    def decode(self, token: str) -> UserMeta:
        payload = jwt.decode(
            token,
            key=self.config.public_key,
            audience=self.config.audience,
            algorithms=["RS256"],
        )

        return UserMeta(
            email=payload["email"],
            system_role=UserSystemRole[payload["role"]],
        )
