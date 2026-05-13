from dataclasses import dataclass

import structlog
from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from prodik.application.interfaces.repositories import UserGrantRepository
from prodik.domain.grant import UserGrant
from prodik.domain.user import UserId

logger = structlog.get_logger()


@dataclass
class UserGrantRepositoryImpl(UserGrantRepository):
    session: AsyncSession

    async def create(self, grant: UserGrant) -> None:
        logger.info("Repository create user grant", grant_id=grant.id)
        await self.session.execute(
            insert(UserGrant).values(
                id=grant.id,
                user_id=grant.user_id,
                role_id=grant.role_id,
                created_at=grant.created_at,
                updated_at=grant.updated_at,
            )
        )

    async def get_all_by_user_id(self, user_id: UserId) -> list[UserGrant]:
        logger.info("Repository get user grants by user id", user_id=user_id)
        result = await self.session.execute(
            select(UserGrant).where(
                UserGrant.user_id == user_id  # type: ignore
            )
        )
        grants = list(result.scalars().all())
        logger.info(
            "Repository fetched grants by user id",
            user_id=user_id,
            count=len(grants),
        )

        return grants
