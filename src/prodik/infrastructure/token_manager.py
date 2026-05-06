from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from uuid import UUID

import jwt

from prodik.application.interfaces.token_manager import TokenManager, UserData
from prodik.domain.user import UserSystemRole
from prodik.infrastructure.config import APIConfig


@dataclass
class TokenManagerImpl(TokenManager):
    _config: APIConfig

    def encode(self, user_id: UUID, user_role: UserSystemRole) -> str:
        now = datetime.now(tz=UTC)
        return jwt.encode(
            {
                "sub": str(user_id),
                "role": user_role,
                "iat": now,
                "exp": now + timedelta(hours=1),
            },
            self._config.secret,
            algorithm="HS256",
        )

    def decode(self, token: str) -> UserData:
        data = jwt.decode(token, self._config.secret, algorithms=["HS256"])
        return UserData(
            uuid=data["sub"],
            role=data["role"],
        )
