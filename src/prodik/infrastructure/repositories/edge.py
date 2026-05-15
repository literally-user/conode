from dataclasses import dataclass

import structlog
from sqlalchemy import and_, delete, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from prodik.application.interfaces.repositories import EdgeRepository
from prodik.domain.context import ContextId
from prodik.domain.edge import Edge, EdgeId
from prodik.domain.node import NodeId

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

    async def get_by_id(self, edge_id: EdgeId) -> Edge | None:
        logger.info("Repository get edge by id", edge_id=edge_id)
        result = await self.session.execute(
            select(Edge).where(
                Edge.id == edge_id  # type: ignore
            )
        )

        edge = result.scalar_one_or_none()
        logger.info("Repository fetched edge by id", found=edge is not None)
        return edge

    async def get_by_nodes_and_context(
        self, node_a_id: NodeId, node_b_id: NodeId, context_id: ContextId
    ) -> Edge | None:
        logger.info(
            "Repository get edge by nodes and context",
            node_a_id=node_a_id,
            node_b_id=node_b_id,
            context_id=context_id,
        )
        result = await self.session.execute(
            select(Edge).where(
                and_(
                    Edge.node_a_id == node_a_id,  # type: ignore
                    Edge.node_b_id == node_b_id,  # type: ignore
                    Edge.context_id == context_id,  # type: ignore
                )
            )
        )

        edge = result.scalar_one_or_none()
        logger.info(
            "Repository fetched edge by nodes and context",
            found=edge is not None,
        )

        return edge

    async def get_all_by_context_id(self, context_id: ContextId) -> list[Edge]:
        logger.info("Repository get edges by context id", context_id=context_id)
        result = await self.session.execute(
            select(Edge).where(
                Edge.context_id == context_id  # type: ignore
            )
        )

        result_edges = list(result.scalars())
        logger.info(
            "Repository fetched edges by context id", found_count=len(result_edges)
        )
        return result_edges
