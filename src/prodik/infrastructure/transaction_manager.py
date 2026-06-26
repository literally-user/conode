import time
import structlog
from uuid import uuid4
from dataclasses import dataclass
from types import TracebackType
from typing import override

from sqlalchemy.ext.asyncio import AsyncSession

from prodik.application.interfaces.transaction_manager import TransactionManager

logger = structlog.get_logger()

@dataclass
class TransactionManagerImpl(TransactionManager):
    _session: AsyncSession

    @override
    async def __aenter__(self) -> None:
        self._start = time.perf_counter()
        self._uuid = uuid4()
        logger.debug(f"Transaction {self._uuid} opened")


    @override
    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        success = True
        if exc is not None:
            success = False
            await self._session.rollback()
        else:
            await self._session.commit()
        
        process_time = time.perf_counter() - self._start

        logger.debug(
            "Processed transaction",
            success=success,
            time=process_time,
        )