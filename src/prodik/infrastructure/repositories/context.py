from dataclasses import dataclass

import structlog
from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from prodik.application.interfaces.repositories import ContextRepository
from prodik.domain.context.model import Context, ContextId

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

    async def get_by_id(self, id: ContextId) -> Context | None:
        logger.info("Repository get context by id", context_id=id)
        result = await self.session.execute(
            select(Context).where(
                Context.id == id  # type: ignore
            )
        )

        context = result.scalar_one_or_none()
        logger.info(
            "Repository fetched context by id", context_id=id, found=context is not None
        )
        return context
