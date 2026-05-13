from dataclasses import dataclass

import structlog
from sqlalchemy import insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from prodik.application.interfaces.repositories import LocalAuthorizationRepository
from prodik.domain.authorization import LocalAuthorization
from prodik.domain.user import UserId

logger = structlog.get_logger()


@dataclass
class LocalAuthorizationRepositoryImpl(LocalAuthorizationRepository):
    session: AsyncSession

    async def create(self, authorization: LocalAuthorization) -> None:
        logger.info(
            "Repository create local authorization", authorization_id=authorization.id
        )
        await self.session.execute(
            insert(LocalAuthorization).values(
                id=authorization.id,
                user_id=authorization.user_id,
                password=authorization.password,
                created_at=authorization.created_at,
                updated_at=authorization.updated_at,
            )
        )

    async def update(self, authorization: LocalAuthorization) -> None:
        logger.info(
            "Repository update local authorization", authorization_id=authorization.id
        )
        await self.session.execute(
            update(LocalAuthorization)
            .where(
                LocalAuthorization.id == authorization.id  # type: ignore
            )
            .values(
                user_id=authorization.user_id,
                password=authorization.password,
            )
        )

    async def get_by_user_id(self, user_id: UserId) -> LocalAuthorization | None:
        logger.info("Repository get local authorization by user id", user_id=user_id)
        result = await self.session.execute(
            select(LocalAuthorization).where(LocalAuthorization.user_id == user_id)  # type: ignore
        )

        authorization = result.scalar_one_or_none()
        logger.info(
            "Repository fetched local authorization by user id",
            user_id=user_id,
            found=authorization is not None,
        )
        return authorization
