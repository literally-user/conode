from dataclasses import dataclass
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


@dataclass
class EntityExistenceService:
    session: AsyncSession

    async def exists(self, entity: Any) -> bool:
        result = await self.session.execute(
            select(entity.__class__).where(entity.__class__.id == entity.id),
        )

        return result.scalar_one_or_none() is not None
