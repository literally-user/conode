from dataclasses import dataclass
from datetime import datetime

import structlog
from redis.asyncio import Redis

from prodik.application.errors import SessionNotFoundError
from prodik.application.interfaces.repositories import SessionRepository
from prodik.domain.authorization import Session, SessionId
from prodik.domain.user import UserId
from prodik.infrastructure.config import CacheConfig

logger = structlog.get_logger()


@dataclass
class SessionRepositoryImpl(SessionRepository):
    client: Redis
    config: CacheConfig

    async def create(self, session: Session) -> None:
        logger.debug("Repository create session", session_id=session.id)
        session_key = f"session:{session.id}"

        host_key = f"host:{session.host}:{session.user_id}"
        token_key = f"token:{session.token}"

        await self.client.hset(
            session_key,
            mapping={  # type: ignore
                "id": str(session.id),
                "user_id": str(session.user_id),
                "token": session.token,
                "host": session.host,
                "created_at": session.created_at.isoformat(),
                "updated_at": session.updated_at.isoformat(),
            },
        )

        await self.client.set(host_key, str(session.id))
        await self.client.set(token_key, str(session.id))

        await self.client.expire(session_key, self.config.ttl)

    async def update(self, prev_token: str, session: Session) -> None:
        logger.debug("Repository update session", session_id=session.id)

        session_key = f"session:{session.id}"
        token_key = f"token:{prev_token}"

        await self.client.hset(
            session_key,
            mapping={  # type: ignore
                "token": session.token,
                "updated_at": session.updated_at.isoformat(),
            },
        )

        await self.client.delete(token_key)
        await self.client.set(token_key, str(session.id))

    async def get_by_token(self, token: str) -> Session:
        logger.debug("Repository get session by token")

        session_id = await self.client.get(f"token:{token}")
        if session_id is None:
            raise SessionNotFoundError(
                "Session not found",
                [{"key": "refresh_token", "value": token}],
            )

        data = await self.client.hgetall(f"session:{session_id}")  # type: ignore
        if data is None:
            raise SessionNotFoundError(
                "Session not found",
                [{"key": "refresh_token", "value": token}],
            )

        session = Session(
            id=SessionId(data["id"]),
            user_id=UserId(data["user_id"]),
            token=data["token"],
            host=data["host"],
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
        )

        logger.debug("Repository fetched session by token", found=session is not None)
        return session

    async def get_by_host_and_user_id(
        self, user_id: UserId, host: str
    ) -> Session | None:
        logger.debug("Repository get session by host", host=host)

        session_id = await self.client.get(f"host:{host}:{user_id}")
        if session_id is None:
            return None

        data = await self.client.hgetall(f"session:{session_id}")  # type: ignore
        if data is None:
            raise SessionNotFoundError(
                "Session not found",
                [{"key": "refresh_token", "value": session_id}],
            )

        session = Session(
            id=SessionId(data["id"]),
            user_id=UserId(data["user_id"]),
            token=data["token"],
            host=data["host"],
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
        )

        logger.debug("Repository fetched session by host", found=session is not None)

        return session
