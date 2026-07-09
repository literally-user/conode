import time
from dataclasses import dataclass
from types import TracebackType
from typing import override
from uuid import uuid4

import structlog
from sqlalchemy.ext.asyncio import AsyncSession
from structlog.contextvars import bind_contextvars

from prodik.application.interfaces.transaction_manager import TransactionManager

logger = structlog.get_logger()


@dataclass
class TransactionManagerImpl(TransactionManager):
    _session: AsyncSession

    @override
    async def __aenter__(self) -> None:
        self._start = time.perf_counter()
        bind_contextvars(transaction_id=uuid4())

    @override
    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        if exc is not None:
            await self._session.rollback()
        else:
            await self._session.commit()

        process_time = time.perf_counter() - self._start

        logger.debug(
            "Processed transaction",
            success=exc is None,
            time=process_time,
        )
