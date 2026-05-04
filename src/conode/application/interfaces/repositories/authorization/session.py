from typing import Protocol

from conode.domain.authorization import Session


class SessionRepository(Protocol):
    async def create(self, session: Session) -> None: ...
