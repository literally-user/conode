from dataclasses import dataclass
from datetime import UTC, datetime
from typing import NewType, Self
from uuid import UUID

from conode.domain.shared import Entity
from conode.domain.user import User, UserId

SessionId = NewType("SessionId", UUID)


@dataclass
class Session(Entity[SessionId]):
    access_token: str
    refresh_token: str
    user_id: UserId
    ip: str

    @classmethod
    def new(
        cls,
        session_id: SessionId,
        refresh_token: str,
        access_token: str,
        user: User,
        ip: str,
    ) -> Self:
        now = datetime.now(UTC)
        return cls(
            id=session_id,
            ip=ip,
            access_token=access_token,
            refresh_token=refresh_token,
            user_id=user.id,
            created_at=now,
            updated_at=now,
        )

    def set_access_token(self, token: str) -> None:
        self.access_token = token

    def set_refresh_token(self, token: str) -> None:
        self.refresh_token = token
