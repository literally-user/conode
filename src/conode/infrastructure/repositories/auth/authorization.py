from dataclasses import dataclass

import structlog
from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from conode.application.errors import AuthorizationNotFoundError
from conode.application.interfaces.repositories import AuthorizationRepository
from conode.domain.auth import Authorization
from conode.domain.user.model import User

logger = structlog.get_logger()


@dataclass
class AuthorizationRepositoryImpl(AuthorizationRepository):
    session: AsyncSession

    async def create(self, authorization: Authorization) -> None:
        logger.debug(
            "Repository create authorization", authorization_id=authorization.id
        )
        await self.session.execute(
            insert(Authorization).values(
                id=authorization.id,
                user_id=authorization.user_id,
                hashed_password=authorization.hashed_password,
                created_at=authorization.created_at,
                updated_at=authorization.updated_at,
            ),
        )

    async def get_by_user(self, user: User) -> Authorization:
        logger.debug("Repository get authorization by user", user_id=user.id)
        authorization = await self.session.execute(
            select(Authorization).where(
                Authorization.user_id == user.id  # type: ignore
            ),
        )

        result = authorization.scalar_one_or_none()
        logger.debug(
            "Repository fetched authorization by user",
            found=result is not None,
        )

        if result is None:
            raise AuthorizationNotFoundError(
                "Authorization associated with this user not found",
                meta=[{"key": "id", "value": user.id}],
            )

        return result
