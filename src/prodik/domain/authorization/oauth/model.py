from dataclasses import dataclass
from datetime import UTC, datetime
from typing import NewType, Self
from uuid import UUID

from prodik.domain.shared import Entity
from prodik.domain.user import User, UserId

OAuthAuthorizationId = NewType("OAuthAuthorizationId", UUID)


@dataclass
class OAuthAuthorization(Entity[OAuthAuthorizationId]):
    user_id: UserId

    @classmethod
    def new(cls, oauth_authorization_id: OAuthAuthorizationId, user: User) -> Self:
        now = datetime.now(UTC)
        return cls(
            id=oauth_authorization_id,
            user_id=user.id,
            created_at=now,
            updated_at=now,
        )
