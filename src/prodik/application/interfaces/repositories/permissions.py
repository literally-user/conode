from typing import Protocol

from prodik.domain.role import RoleId, RolePermission


class RolePermissionsRepository(Protocol):
    async def create_all(self, permissions: list[RolePermission]) -> None: ...
    async def get_all_by_role_id(self, role_id: RoleId) -> list[RolePermission]: ...
