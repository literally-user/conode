from dataclasses import dataclass
from datetime import UTC, datetime
from typing import NewType, Self
from uuid import UUID

from conode.domain.shared import Entity
from conode.domain.user import User, UserId

SessionId = NewType("SessionId", UUID)


@dataclass
class Session(Entity[SessionId]):
    refresh_token: str
    user_id: UserId
    ip: str

    @classmethod
    def new(
        cls,
        session_id: SessionId,
        refresh_token: str,
        user: User,
        ip: str,
    ) -> Self:
        now = datetime.now(UTC)
        return cls(
            id=session_id,
            ip=ip,
            refresh_token=refresh_token,
            user_id=user.id,
            created_at=now,
            updated_at=now,
        )

    def set_refresh_token(self, token: str) -> None:
        self.refresh_token = token
