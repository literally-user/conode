from typing import Protocol

from prodik.domain.node import Node, NodeAssociation


class NodeRepository(Protocol):
    async def create(self, node: Node) -> None: ...


class NodeAssociationRepository(Protocol):
    async def create(self, node_association: NodeAssociation) -> None: ...
