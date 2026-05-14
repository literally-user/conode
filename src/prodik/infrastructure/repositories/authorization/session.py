from dataclasses import dataclass

import structlog
from sqlalchemy import insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from prodik.application.interfaces.repositories import SessionRepository
from prodik.domain.authorization import Session

logger = structlog.get_logger()


@dataclass
class SessionRepositoryImpl(SessionRepository):
    session: AsyncSession

    async def create(self, session: Session) -> None:
        logger.info("Repository create session", session_id=session.id)
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
        logger.info("Repository update session", session_id=session.id)
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
        logger.info("Repository get session by token")
        result = await self.session.execute(
            select(Session).where(Session.token == token)  # type: ignore
        )

        session = result.scalar_one_or_none()
        logger.info("Repository fetched session by token", found=session is not None)
        return session

    async def get_by_host(self, host: str) -> Session | None:
        logger.info("Repository get session by host", host=host)
        result = await self.session.execute(
            select(Session).where(Session.host == host)  # type: ignore
        )

        session = result.scalar_one_or_none()
        logger.info("Repository fetched session by host", found=session is not None)
        return session
