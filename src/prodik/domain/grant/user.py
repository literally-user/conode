from dataclasses import dataclass
from datetime import UTC, datetime
from typing import NewType, Self
from uuid import UUID

from prodik.domain.role import Role, RoleId
from prodik.domain.shared import Entity
from prodik.domain.user import User, UserId

UserGrantId = NewType("UserGrantId", UUID)


@dataclass
class UserGrant(Entity[UserGrantId]):
    user_id: UserId
    role_id: RoleId

    @classmethod
    def new(cls, id: UserGrantId, role: Role, user: User) -> Self:
        now = datetime.now(UTC)
        return cls(
            id=id,
            user_id=user.id,
            role_id=role.id,
            created_at=now,
            updated_at=now,
        )
