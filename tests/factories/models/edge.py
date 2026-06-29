from dataclasses import dataclass
from uuid import uuid4

from prodik.application.interfaces.repositories import EdgeRepository
from prodik.application.interfaces.transaction_manager import TransactionManager
from prodik.domain.company import Company
from prodik.domain.context import Context
from prodik.domain.edge import Edge, EdgeId
from prodik.domain.node import Node


@dataclass
class EdgeFactory:
    edge_repository: EdgeRepository
    transaction_manager: TransactionManager

    async def build(
        self, *, node_a: Node, node_b: Node, context: Context, company: Company
    ) -> Edge:
        async with self.transaction_manager:
            edge = Edge.new(
                edge_id=EdgeId(uuid4()),
                node_a=node_a,
                node_b=node_b,
                context=context,
                company=company,
                weight=0,
            )

            await self.edge_repository.create(edge)

            return edge
