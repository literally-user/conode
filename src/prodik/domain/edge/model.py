from dataclasses import dataclass
from datetime import UTC, datetime
from typing import NewType, Self
from uuid import UUID

from prodik.domain.company import Company, CompanyId
from prodik.domain.context import Context, ContextId
from prodik.domain.edge.errors import EdgeCannotConnectTwoSameNodesError
from prodik.domain.node import Node, NodeId
from prodik.domain.shared import Entity

EdgeId = NewType("EdgeId", UUID)


@dataclass
class Edge(Entity[EdgeId]):
    company_id: CompanyId
    context_id: ContextId
    node_a_id: NodeId
    node_b_id: NodeId
    weight: float

    @classmethod
    def new(
        cls,
        edge_id: EdgeId,
        node_a: Node,
        node_b: Node,
        company: Company,
        context: Context,
        weight: float,
    ) -> Self:
        if node_a == node_b:
            raise EdgeCannotConnectTwoSameNodesError(
                "Edge cannot connect two same nodes",
                [
                    {"key": "node_a", "value": node_a},
                    {"key": "node_b", "value": node_b},
                ],
            )

        now = datetime.now(UTC)
        return cls(
            id=edge_id,
            company_id=company.id,
            context_id=context.id,
            node_a_id=node_a.id,
            node_b_id=node_b.id,
            weight=weight,
            created_at=now,
            updated_at=now,
        )

    def increment_weight(self) -> None:
        self.weight += 1

    def decrement_weight(self) -> None:
        self.weight -= 1

    def update_weight(self, weight: float) -> None:
        self.weight = weight
