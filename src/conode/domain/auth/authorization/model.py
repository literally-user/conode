from dataclasses import dataclass
from datetime import UTC, datetime
from typing import NewType, Self
from uuid import UUID

from conode.domain.shared import Entity
from conode.domain.user import User, UserId

AuthorizationId = NewType("AuthorizationId", UUID)


@dataclass
class Authorization(Entity[AuthorizationId]):
    hashed_password: str
    user_id: UserId

    @classmethod
    def new(
        cls, authorization_id: AuthorizationId, hashed_password: str, user: User
    ) -> Self:
        now = datetime.now(UTC)
        return cls(
            id=authorization_id,
            hashed_password=hashed_password,
            user_id=user.id,
            created_at=now,
            updated_at=now,
        )
