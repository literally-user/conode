from typing import Protocol

from prodik.domain.grant import UserGrant
from prodik.domain.role import RoleId
from prodik.domain.user import UserId


class UserGrantRepository(Protocol):
    async def create(self, grant: UserGrant) -> None: ...
    async def delete(self, grant: UserGrant) -> None: ...
    async def get_all_by_user_id(self, user_id: UserId) -> list[UserGrant]: ...
    async def get_by_user_and_role_id(
        self, user_id: UserId, role_id: RoleId
    ) -> UserGrant | None: ...
