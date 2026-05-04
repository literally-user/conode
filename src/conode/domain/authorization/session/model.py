from dataclasses import dataclass
from datetime import UTC, datetime
from typing import NewType
from uuid import UUID

from conode.domain.shared import Entity
from conode.domain.user import User, UserId

SessionId = NewType("SessionId", UUID)


@dataclass
class Session(Entity[SessionId]):
    user_id: UserId
    host: str

    @classmethod
    def new(cls, id: SessionId, user: User, host: str) -> "Session":
        now = datetime.now(UTC)
        return Session(
            id=id,
            host=host,
            user_id=user.id,
            created_at=now,
            updated_at=now,
        )
