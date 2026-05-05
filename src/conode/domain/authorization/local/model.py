from dataclasses import dataclass
from datetime import UTC, datetime
from typing import NewType
from uuid import UUID

from conode.domain.shared import Entity
from conode.domain.user import User, UserId

LocalAuthorizationId = NewType("LocalAuthorizationId", UUID)


@dataclass
class LocalAuthorization(Entity[LocalAuthorizationId]):
    user_id: UserId
    password: str

    @classmethod
    def new(
        cls, id: LocalAuthorizationId, user: User, password: str
    ) -> "LocalAuthorization":
        now = datetime.now(UTC)
        return LocalAuthorization(
            id=id,
            user_id=user.id,
            password=password,
            created_at=now,
            updated_at=now,
        )

    def update_password(self, password: str) -> None:
        self.password = password
