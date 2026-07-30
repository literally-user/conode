from dataclasses import dataclass
from uuid import uuid4

from conode.application.interfaces.repositories import EdgeRepository
from conode.application.interfaces.transaction_manager import TransactionManager
from conode.domain.company import Company
from conode.domain.context import Context
from conode.domain.edge import Edge, EdgeId
from conode.domain.node import Node


@dataclass
class EdgeFactory:
    edge_repository: EdgeRepository
    transaction_manager: TransactionManager

    async def build(
        self,
        *,
        node_a: Node,
        node_b: Node,
        context: Context,
        company: Company,
        weight: int = 0,
    ) -> Edge:
        async with self.transaction_manager:
            edge = Edge.new(
                edge_id=EdgeId(uuid4()),
                node_a=node_a,
                node_b=node_b,
                context=context,
                company=company,
                weight=weight,
            )

            await self.edge_repository.create(edge)

            return edge
