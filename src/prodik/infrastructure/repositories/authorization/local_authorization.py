from dataclasses import dataclass

from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession

from prodik.application.interfaces.repositories import LocalAuthorizationRepository
from prodik.domain.authorization import LocalAuthorization


@dataclass
class LocalAuthorizationRepositoryImpl(LocalAuthorizationRepository):
    session: AsyncSession

    async def create(self, authorization: LocalAuthorization) -> None:
        await self.session.execute(
            insert(LocalAuthorization).values(
                id=authorization.id,
                user_id=authorization.user_id,
                hashed_password=authorization.password,
                created_at=authorization.created_at,
                updated_at=authorization.updated_at,
            )
        )
