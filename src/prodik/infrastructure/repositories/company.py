from dataclasses import dataclass

from sqlalchemy import insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from prodik.application.interfaces.repositories import CompanyRepository
from prodik.domain.company.model import Company, CompanyId, CompanyName
from prodik.domain.user import UserId


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

    async def update(self, company: Company) -> None:
        await self.session.execute(
            update(Company)
            .where(
                Company.id == company.id  # type: ignore
            )
            .values(
                name=company.name,
                description=company.description,
                verified=company.verified,
                owner_id=company.owner_id,
            )
        )

    async def get_by_name(self, name: CompanyName) -> Company | None:
        result = await self.session.execute(
            select(Company).where(
                Company.name == name  # type: ignore
            )
        )

        return result.scalar_one_or_none()

    async def get_by_id(self, id: CompanyId) -> Company | None:
        result = await self.session.execute(
            select(Company).where(
                Company.id == id  # type: ignore
            )
        )

        return result.scalar_one_or_none()

    async def get_by_user_id(self, id: UserId) -> Company | None:
        result = await self.session.execute(
            select(Company)
            .where(
                Company.owner_id == id  # type: ignore
            )
            .limit(1)
        )

        return result.scalar_one_or_none()
