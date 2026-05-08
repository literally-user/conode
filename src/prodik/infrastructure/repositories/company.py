from dataclasses import dataclass

from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from prodik.application.interfaces.repositories import CompanyRepository
from prodik.domain.company.model import Company, CompanyName


@dataclass
class CompanyRepositoryImpl(CompanyRepository):
    session: AsyncSession

    async def create(self, company: Company) -> None:
        await self.session.execute(
            insert(Company).values(
                id=company.id,
                name=company.name,
                description=company.description,
                verified=company.verified,
                owner_id=company.owner_id,
                created_at=company.created_at,
                updated_at=company.updated_at,
            )
        )

    async def get_by_name(self, name: CompanyName) -> Company | None:
        result = await self.session.execute(
            select(Company).where(
                Company.name == name  # type: ignore
            )
        )

        return result.scalar_one_or_none()
