from typing import Protocol

from prodik.domain.company import Company, CompanyName


class CompanyRepository(Protocol):
    async def get_by_name(self, name: CompanyName) -> Company | None: ...
    async def create(self, company: Company) -> None: ...
