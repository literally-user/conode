from typing import Protocol

from prodik.domain.authorization import Session


class SessionRepository(Protocol):
    async def create(self, session: Session) -> None: ...
