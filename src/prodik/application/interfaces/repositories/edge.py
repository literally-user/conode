from typing import Protocol

from prodik.domain.edge import Edge


class EdgeRepository(Protocol):
    async def create(self, edge: Edge) -> None: ...
