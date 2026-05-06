from dataclasses import dataclass

from sqlalchemy import insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from prodik.application.interfaces.repositories import LocalAuhthorizationRepository
from prodik.domain.authorization.local import LocalAuthorization
from prodik.domain.user import UserId


@dataclass
class LocalAuhthorizationRepositoryImpl(LocalAuhthorizationRepository):
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

    async def update(self, authorization: LocalAuthorization) -> None:
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
        result = await self.session.execute(
            select(LocalAuthorization).where(
                LocalAuthorization.user_id == user_id  # type: ignore
            )
        )

        return result.scalar_one_or_none()
