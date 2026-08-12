from dataclasses import dataclass
from types import TracebackType
from typing import override

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from conode.application.interfaces.transaction_manager import TransactionManager

logger = structlog.get_logger()


@dataclass
class TransactionManagerImpl(TransactionManager):
    _session: AsyncSession

    @override
    async def __aenter__(self) -> None: ...

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
