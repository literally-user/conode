from typing import Protocol

from conode.domain.authorization import LocalAuthorization


class LocalAuhthorizationRepository(Protocol):
    async def create(self, authorization: LocalAuthorization) -> None: ...
