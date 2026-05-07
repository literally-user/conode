from dataclasses import dataclass

from sqlalchemy import insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from prodik.application.interfaces.repositories import SessionRepository
from prodik.domain.authorization import Session


@dataclass
class SessionRepositoryImpl(SessionRepository):
    session: AsyncSession

    async def create(self, session: Session) -> None:
        await self.session.execute(
            insert(Session).values(
                id=session.id,
                user_id=session.user_id,
                token=session.token,
                host=session.host,
                created_at=session.created_at,
                updated_at=session.updated_at,
            )
        )

    async def update(self, session: Session) -> None:
        await self.session.execute(
            update(Session)
            .where(
                Session.id == session.id  # type: ignore
            )
            .values(
                user_id=session.user_id,
                token=session.token,
                host=session.host,
                updated_at=session.updated_at,
            )
        )

    async def get_by_token(self, token: str) -> Session | None:
        result = await self.session.execute(
            select(Session).where(Session.token == token)  # type: ignore
        )

        return result.scalar_one_or_none()

    async def get_by_host(self, host: str) -> Session | None:
        result = await self.session.execute(
            select(Session).where(Session.host == host)  # type: ignore
        )

        return result.scalar_one_or_none()
