from typing import Protocol

from conode.domain.auth import Authorization
from conode.domain.user import User


class AuthorizationRepository(Protocol):
    async def create(self, authorization: Authorization) -> None: ...
    async def get_by_user(self, user: User) -> Authorization: ...
