from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

import jwt

from conode.application.authorization.errors import InvalidTokenError
from conode.application.interfaces.token_managers import AccessTokenManager, UserMeta
from conode.domain.user.model import User
from conode.infrastructure.config import CertsConfig


@dataclass
class AccessTokenManagerImpl(AccessTokenManager):
    config: CertsConfig

    def encode(self, user: User) -> tuple[str, int]:
        now = datetime.now(UTC)
        token = jwt.encode(
            {
                "sub": user.id,
                "iat": int(now.timestamp()),
                "exp": int(
                    (now + timedelta(seconds=self.config.expires_in)).timestamp()
                ),
            },
            self.config.private_key,
            algorithm="RS256",
        )

        return token, self.config.expires_in

    def decode(self, token: str) -> UserMeta:
        try:
            content = jwt.decode(token, self.config.public_key, algorithms=["RS256"])
        except jwt.exceptions.PyJWKError as e:
            raise InvalidTokenError(
                "Invalid access token", [{"key": "authorization", "value": token}]
            ) from e

        return UserMeta(user_id=content["sub"])
