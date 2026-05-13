from dataclasses import dataclass

import structlog
from sqlalchemy import delete, insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from prodik.application.interfaces.repositories import ContextRepository
from prodik.domain.company import CompanyId
from prodik.domain.context import Context, ContextId

logger = structlog.get_logger()


@dataclass
class ContextRepositoryImpl(ContextRepository):
    session: AsyncSession

    async def create(self, context: Context) -> None:
        logger.info("Repository create context", context_id=context.id)
        await self.session.execute(
            insert(Context).values(
                id=context.id,
                name=context.name,
                description=context.description,
                company_id=context.company_id,
                updated_at=context.updated_at,
                created_at=context.created_at,
            )
        )

    async def get_by_id(self, context_id: ContextId) -> Context | None:
        logger.info("Repository get context by id", context_id=context_id)
        result = await self.session.execute(
            select(Context).where(
                Context.id == context_id  # type: ignore
            )
        )

        context = result.scalar_one_or_none()
        logger.info(
            "Repository fetched context by id",
            context_id=context_id,
            found=context is not None,
        )
        return context

    async def delete(self, context: Context) -> None:
        logger.info("Repository delete context", context_id=context.id)
        await self.session.execute(
            delete(Context).where(
                Context.id == context.id  # type: ignore
            )
        )

    async def get_all_by_company_id(self, company_id: CompanyId) -> list[Context]:
        logger.info("Repository get groups by contexts id", company_id=company_id)
        result = await self.session.execute(
            select(Context).where(
                Context.company_id == company_id  # type: ignore
            )
        )

        return list(result.scalars())
