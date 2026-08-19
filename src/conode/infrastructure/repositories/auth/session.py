from dataclasses import dataclass

import structlog
from sqlalchemy import and_, insert, select, update
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from conode.application.errors import SessionNotFoundError
from conode.application.interfaces.repositories import SessionRepository
from conode.domain.auth import Session
from conode.domain.user import User

logger = structlog.get_logger()


@dataclass
class SessionRepositoryImpl(SessionRepository):
    session: AsyncSession

    async def create(self, session: Session) -> None:
        logger.debug("Repository create session", session_id=session.id)
        await self.session.execute(
            insert(Session).values(
                id=session.id,
                ip=session.ip,
                user_id=session.user_id,
                refresh_token=session.refresh_token,
                created_at=session.created_at,
                updated_at=session.updated_at,
            ),
        )

    async def upsert(self, session: Session) -> None:
        logger.debug("Repository upsert session", session_id=session.id)
        stmt = pg_insert(Session).values(
            id=session.id,
            ip=session.ip,
            user_id=session.user_id,
            refresh_token=session.refresh_token,
            created_at=session.created_at,
            updated_at=session.updated_at,
        )
        stmt = stmt.on_conflict_do_update(
            constraint="uq_session_record_user_id_ip",
            set_={
                "refresh_token": stmt.excluded.refresh_token,
                "updated_at": stmt.excluded.updated_at,
            },
        )
        await self.session.execute(stmt)

    async def update(self, session: Session) -> None:
        logger.debug("Repository update session", session_id=session.id)
        await self.session.execute(
            update(Session)
            .where(
                Session.id == session.id,  # type: ignore
            )
            .values(
                refresh_token=session.refresh_token,
                updated_at=session.updated_at,
            ),
        )

    async def get_by_refresh_token(self, token: str) -> Session:
        logger.debug("Repository get session by refresh token", token=token)
        session = await self.session.execute(
            select(Session).where(
                Session.refresh_token == token  # type: ignore
            ),
        )

        result = session.scalar_one_or_none()
        logger.debug(
            "Repository fetched session by ip and user",
            found=result is not None,
        )

        if result is None:
            raise SessionNotFoundError(
                "Session associated with this refresh token not found",
                meta=[{"key": "token", "value": token}],
            )

        return result

    async def get_by_ip_and_user(self, user: User, ip: str) -> Session | None:
        logger.debug("Repository get session by ip and user", ip=ip, user_id=user.id)
        session = await self.session.execute(
            select(Session).where(
                and_(
                    Session.ip == ip,  # type: ignore
                    Session.user_id == user.id,  # type: ignore
                )
            ),
        )

        result = session.scalar_one_or_none()
        logger.debug(
            "Repository fetched session by ip and user",
            found=result is not None,
        )

        return result
