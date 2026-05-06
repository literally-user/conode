from dataclasses import dataclass

from sqlalchemy import insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from conode.application.interfaces.repositories import SessionRepository
from conode.domain.authorization.session import Session


@dataclass
class SessionRepositoryImpl(SessionRepository):
    session: AsyncSession

    async def create(self, session: Session) -> None:
        await self.session.execute(
            insert(Session).values(
                id=session.id,
                host=session.host,
                token=session.token,
                user_id=session.user_id,
                token_revision=session.token_revision,
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
                host=session.host,
                token=session.token,
                user_id=session.user_id,
                token_revision=session.token_revision,
            )
        )

    async def get_by_host(self, host: str) -> Session | None:
        result = await self.session.execute(
            select(Session).where(
                Session.host == host  # type: ignore
            )
        )

        return result.scalar_one_or_none()
