from dataclasses import dataclass
from datetime import UTC, datetime
from typing import NewType
from uuid import UUID

from conode.domain.shared import Entity
from conode.domain.user import User, UserId

OAuthAuthorizationId = NewType("OAuthAuthorizationId", UUID)


@dataclass
class OAuthAuthorization(Entity[OAuthAuthorizationId]):
    user_id: UserId

    @classmethod
    def new(cls, id: OAuthAuthorizationId, user: User) -> "OAuthAuthorization":
        now = datetime.now(UTC)
        return OAuthAuthorization(
            id=id,
            user_id=user.id,
            created_at=now,
            updated_at=now,
        )
