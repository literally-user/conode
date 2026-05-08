from typing import Protocol

from prodik.domain.group import Group, GroupId


class GroupRepository(Protocol):
    async def create(self, group: Group) -> None: ...
    async def get_by_id(self, id: GroupId) -> Group | None: ...
