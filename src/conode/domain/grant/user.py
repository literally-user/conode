from dataclasses import dataclass
from datetime import UTC, datetime
from typing import NewType
from uuid import UUID

from conode.domain.role import Role, RoleId
from conode.domain.shared import Entity
from conode.domain.user import User, UserId

UserGrantId = NewType("UserGrantId", UUID)


@dataclass
class UserGrant(Entity[UserGrantId]):
    user_id: UserId
    role_id: RoleId

    @classmethod
    def new(cls, id: UserGrantId, role: Role, user: User) -> "UserGrant":
        now = datetime.now(UTC)
        return UserGrant(
            id=id,
            user_id=user.id,
            role_id=role.id,
            created_at=now,
            updated_at=now,
        )
