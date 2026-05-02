from dataclasses import dataclass
from datetime import UTC, datetime
from typing import NewType
from uuid import UUID

from conode.domain.company import Company, CompanyId
from conode.domain.node import Node, NodeId
from conode.domain.shared import Entity

EdgeId = NewType("EdgeId", UUID)


@dataclass
class Edge(Entity[EdgeId]):
    company_id: CompanyId
    node_a_id: NodeId
    node_b_id: NodeId

    @classmethod
    def new(cls, id: EdgeId, node_a: Node, node_b: Node, company: Company) -> "Edge":
        now = datetime.now(UTC)
        return Edge(
            id=id,
            company_id=company.id,
            node_a_id=node_a.id,
            node_b_id=node_b.id,
            created_at=now,
            updated_at=now,
        )
