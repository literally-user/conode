from typing import Protocol

from conode.domain.contract import Contract


class ContractRepository(Protocol):
    async def create(self, contract: Contract) -> None: ...
