from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

import jwt

from prodik.application.interfaces.token_managers import (
    AccessTokenManager,
    AccessTokenManagerResponse,
    UserMeta,
)
from prodik.domain.user import User
from prodik.infrastructure.config import APIConfig


@dataclass
class AccessTokenManagerImpl(AccessTokenManager):
    _config: APIConfig

    def encode(self, user: User) -> AccessTokenManagerResponse:
        now = datetime.now(tz=UTC)
        token = jwt.encode(
            {
                "sub": str(user.id),
                "system_role": user.system_role,
                "revision": user.token_revision,
                "iat": now,
                "exp": now + timedelta(seconds=self._config.expires_in),
            },
            self._config.secret,
            algorithm="HS256",
        )
        return AccessTokenManagerResponse(
            token=token, expires_in=self._config.expires_in
        )

    def decode(self, token: str) -> UserMeta:
        data = jwt.decode(token, self._config.secret, algorithms=["HS256"])
        return UserMeta(
            system_role=data["system_role"],
            user_id=data["user_id"],
            revision=data["revision"],
        )
