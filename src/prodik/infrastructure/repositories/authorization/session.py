from dataclasses import dataclass

from sqlalchemy import insert
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
