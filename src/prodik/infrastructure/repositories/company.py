from dataclasses import dataclass

import structlog
from sqlalchemy import insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from prodik.application.interfaces.repositories import CompanyRepository
from prodik.domain.company.model import Company, CompanyId, CompanyName
from prodik.domain.user import UserId

logger = structlog.get_logger()


@dataclass
class CompanyRepositoryImpl(CompanyRepository):
    session: AsyncSession

    async def create(self, company: Company) -> None:
        logger.info("Repository create company", company_id=company.id)
        await self.session.execute(
            insert(Company).values(
                id=company.id,
                name=company.name,
                description=company.description,
                verified=company.verified,
                owner_id=company.owner_id,
                created_at=company.created_at,
                updated_at=company.updated_at,
            ),
        )

    async def update(self, company: Company) -> None:
        logger.info("Repository update company", company_id=company.id)
        await self.session.execute(
            update(Company)
            .where(
                Company.id == company.id,  # type: ignore
            )
            .values(
                name=company.name,
                description=company.description,
                verified=company.verified,
                owner_id=company.owner_id,
            ),
        )

    async def get_by_name(self, name: CompanyName) -> Company | None:
        logger.info("Repository get company by name", company_name=name)
        result = await self.session.execute(
            select(Company).where(
                Company.name == name,  # type: ignore
            ),
        )

        company = result.scalar_one_or_none()
        logger.info("Repository fetched company by name", found=company is not None)
        return company

    async def get_by_id(self, company_id: CompanyId) -> Company | None:
        logger.info("Repository get company by id", company_id=company_id)
        result = await self.session.execute(
            select(Company).where(
                Company.id == company_id,  # type: ignore
            ),
        )

        company = result.scalar_one_or_none()
        logger.info(
            "Repository fetched company by id",
            found=company is not None,
        )
        return company

    async def get_by_user_id(self, user_id: UserId) -> Company | None:
        logger.info("Repository get company by user id", user_id=user_id)
        result = await self.session.execute(
            select(Company)
            .where(
                Company.owner_id == user_id,  # type: ignore
            )
            .limit(1),
        )

        company = result.scalar_one_or_none()
        logger.info(
            "Repository fetched company by user id",
            found=company is not None,
        )
        return company
