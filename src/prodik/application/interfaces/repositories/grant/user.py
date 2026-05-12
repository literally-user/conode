from typing import Protocol

from prodik.domain.grant import UserGrant


class UserGrantRepository(Protocol):
    async def create(self, grant: UserGrant) -> None: ...
