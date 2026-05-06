from typing import Protocol

from prodik.domain.company import Company


class CompanyRepository(Protocol):
    async def create(self, company: Company) -> None: ...
    async def get_by_name(self, name: str) -> Company | None: ...
