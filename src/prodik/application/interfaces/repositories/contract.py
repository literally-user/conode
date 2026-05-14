from typing import Protocol

from prodik.domain.contract import Contract


class ContractRepository(Protocol):
    async def create(self, contract: Contract) -> None: ...
