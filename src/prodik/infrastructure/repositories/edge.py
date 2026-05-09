from dataclasses import dataclass

import structlog
from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession

from prodik.application.interfaces.repositories import EdgeRepository
from prodik.domain.edge.model import Edge

logger = structlog.get_logger()


@dataclass
class EdgeRepositoryImpl(EdgeRepository):
    session: AsyncSession

    async def create(self, edge: Edge) -> None:
        logger.info("Repository create edge", edge_id=edge.id)
        await self.session.execute(
            insert(Edge).values(
                id=edge.id,
                company_id=edge.company_id,
                context_id=edge.context_id,
                node_a_id=edge.node_a_id,
                node_b_id=edge.node_b_id,
                created_at=edge.created_at,
                updated_at=edge.updated_at,
                weight=edge.weight,
            )
        )
