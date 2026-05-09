from dataclasses import dataclass

import structlog
from sqlalchemy import delete, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from prodik.application.interfaces.repositories import EdgeRepository
from prodik.domain.edge.model import Edge, EdgeId

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

    async def delete(self, edge: Edge) -> None:
        logger.info("Repository delete edge", edge_id=edge.id)
        await self.session.execute(
            delete(Edge).where(
                Edge.id == edge.id  # type: ignore
            )
        )

    async def update(self, edge: Edge) -> None:
        logger.info("Repository update edge", edge_id=edge.id)
        await self.session.execute(
            update(Edge)
            .where(
                Edge.id == edge.id  # type: ignore
            )
            .values(
                weight=edge.weight,
                updated_at=edge.updated_at,
            )
        )

    async def get_by_id(self, id: EdgeId) -> Edge | None:
        logger.info("Repository get edge by id", edge_id=id)
        result = await self.session.execute(
            select(Edge).where(
                Edge.id == id  # type: ignore
            )
        )

        edge = result.scalar_one_or_none()
        logger.info("Repository fetched edge by id", edge_id=id, found=edge is not None)
        return edge
