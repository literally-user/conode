from typing import Protocol

from prodik.domain.authorization import LocalAuthorization
from prodik.domain.user import UserId


class LocalAuthorizationRepository(Protocol):
    async def create(self, authorization: LocalAuthorization) -> None: ...
    async def get_by_user_id(self, id: UserId) -> LocalAuthorization | None: ...
