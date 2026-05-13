from typing import Protocol

from prodik.domain.role import Role, RoleId


class RoleRepository(Protocol):
    async def create(self, role: Role) -> None: ...
    async def get_all_by_ids(self, ids: list[RoleId]) -> list[Role]: ...
