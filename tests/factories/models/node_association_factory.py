from dataclasses import dataclass
from uuid import uuid4

from prodik.application.interfaces.repositories import NodeAssociationRepository
from prodik.domain.group import Group
from prodik.domain.node import Node, NodeAssociation, NodeAssociationId


@dataclass(slots=True)
class NodeAssociationFactory:
    node_association_repository: NodeAssociationRepository

    async def create_association(self, node: Node, group: Group) -> NodeAssociation:
        association = NodeAssociation.new(
            node_association_id=NodeAssociationId(uuid4()),
            node=node,
            group=group,
        )
        await self.node_association_repository.create(association)
        return association
