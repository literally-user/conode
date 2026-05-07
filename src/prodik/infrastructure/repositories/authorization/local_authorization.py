from dataclasses import dataclass

from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from prodik.application.interfaces.repositories import LocalAuthorizationRepository
from prodik.domain.authorization import LocalAuthorization
from prodik.domain.user import UserId


@dataclass
class LocalAuthorizationRepositoryImpl(LocalAuthorizationRepository):
    session: AsyncSession

    async def create(self, authorization: LocalAuthorization) -> None:
        await self.session.execute(
            insert(LocalAuthorization).values(
                id=authorization.id,
                user_id=authorization.user_id,
                password=authorization.password,
                created_at=authorization.created_at,
                updated_at=authorization.updated_at,
            )
        )

    async def get_by_user_id(self, id: UserId) -> LocalAuthorization | None:
        result = await self.session.execute(
            select(LocalAuthorization).where(LocalAuthorization.user_id == id)  # type: ignore
        )

        return result.scalar_one_or_none()
