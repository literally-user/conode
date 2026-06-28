from dataclasses import dataclass
from uuid import uuid4

from prodik.application.interfaces.repositories import (
    NodeAssociationRepository,
    NodeRepository,
)
from prodik.application.interfaces.transaction_manager import TransactionManager
from prodik.domain.company import Company
from prodik.domain.group import Group
from prodik.domain.node import Node, NodeAssociation, NodeAssociationId, NodeId
from tests.factories.common import generate_random_string


@dataclass
class NodeFactory:
    transaction_manager: TransactionManager
    node_association_repository: NodeAssociationRepository
    node_repository: NodeRepository

    async def build(self, company: Company, group: Group) -> Node:
        async with self.transaction_manager:
            node = Node.new(
                node_id=NodeId(uuid4()),
                company=company,
                name=generate_random_string(),
                description=generate_random_string(),
            )

            node_association = NodeAssociation.new(
                node_association_id=NodeAssociationId(uuid4()),
                node=node,
                group=group,
            )

            await self.node_repository.create(node)
            await self.node_association_repository.create(node_association)

            return node
