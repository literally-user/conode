from typing import Protocol

from prodik.domain.authorization import LocalAuthorization


class LocalAuthorizationRepository(Protocol):
    async def create(self, authorization: LocalAuthorization) -> None: ...
