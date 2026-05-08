from dataclasses import dataclass

from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession

from prodik.application.interfaces.repositories import (
    NodeAssociationRepository,
    NodeRepository,
)
from prodik.domain.node.model import Node, NodeAssociation


@dataclass
class NodeRepositoryImpl(NodeRepository):
    session: AsyncSession

    async def create(self, node: Node) -> None:
        await self.session.execute(
            insert(Node).values(
                id=node.id,
                name=node.name,
                description=node.description,
                company_id=node.company_id,
                created_at=node.created_at,
                updated_at=node.updated_at,
            )
        )


@dataclass
class NodeAssociationRepositoryImpl(NodeAssociationRepository):
    session: AsyncSession

    async def create(self, node_association: NodeAssociation) -> None:
        await self.session.execute(
            insert(NodeAssociation).values(
                id=node_association.id,
                group_id=node_association.group_id,
                node_id=node_association.node_id,
                created_at=node_association.created_at,
                updated_at=node_association.updated_at,
            )
        )
