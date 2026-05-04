from typing import Protocol

from conode.domain.authorization import LocalAuthorization
from conode.domain.user import UserId


class LocalAuhthorizationRepository(Protocol):
    async def create(self, authorization: LocalAuthorization) -> None: ...
    async def get_by_user_id(self, user_id: UserId) -> LocalAuthorization | None: ...
