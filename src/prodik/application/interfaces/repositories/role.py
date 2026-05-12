from typing import Protocol

from prodik.domain.role import Role
from prodik.domain.user import UserId


class RoleRepository(Protocol):
    async def create(self, role: Role) -> None: ...
    async def get_all_by_user_id(self, user_id: UserId) -> list[Role]: ...
