from dataclasses import dataclass
from datetime import datetime

import structlog
from redis.asyncio import Redis

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
        logger.info("Repository create session", session_id=session.id)
        session_key = f"session:{session.token}"
        host_key = f"host:{session.host}"

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

        await self.client.set(host_key, session.token)

        await self.client.expire(session_key, self.config.ttl)

    async def update(self, session: Session) -> None:
        logger.info("Repository update session", session_id=session.id)
        session_key = f"session:{session.token}"
        await self.client.hset(
            session_key,
            mapping={  # type: ignore
                "token": session.token,
                "updated_at": session.updated_at.isoformat(),
            },
        )

    async def get_by_token(self, token: str) -> Session | None:
        logger.info("Repository get session by token")

        data = await self.client.hgetall(f"session:{token}")  # type: ignore
        if not data:
            return None

        session = Session(
            id=SessionId(data["id"]),
            user_id=UserId(data["user_id"]),
            token=data["token"],
            host=data["host"],
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
        )

        logger.info("Repository fetched session by token", found=session is not None)
        return session

    async def get_by_host(self, host: str) -> Session | None:
        logger.info("Repository get session by host", host=host)

        token = await self.client.get(f"host:{host}")
        if token is None:
            return None

        data = await self.client.hgetall(f"session:{token}")  # type: ignore

        session = Session(
            id=SessionId(data["id"]),
            user_id=UserId(data["user_id"]),
            token=data["token"],
            host=data["host"],
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
        )

        logger.info("Repository fetched session by host", found=session is not None)

        return session
