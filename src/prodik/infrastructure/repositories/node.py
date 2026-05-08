from dataclasses import dataclass

from sqlalchemy import delete, insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from prodik.application.interfaces.repositories import (
    NodeAssociationRepository,
    NodeRepository,
)
from prodik.domain.node.model import Node, NodeAssociation, NodeAssociationId, NodeId


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

    async def get_all_by_ids(self, nodes: list[NodeId]) -> list[Node]:
        if not nodes:
            return []

        result = await self.session.execute(
            select(Node).where(
                Node.id.in_(nodes)  # type: ignore
            )
        )

        return list(result.scalars().all())


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

    async def delete(self, node_association: NodeAssociation) -> None:
        await self.session.execute(
            delete(NodeAssociation).where(
                NodeAssociation.id == node_association.id  # type: ignore
            )
        )

    async def get_by_id(self, id: NodeAssociationId) -> NodeAssociation | None:
        result = await self.session.execute(
            select(NodeAssociation).where(
                NodeAssociation.id == id  # type: ignore
            )
        )

        return result.scalar_one_or_none()

    async def create_all(self, node_association: list[NodeAssociation]) -> None:
        if not node_association:
            return

        await self.session.execute(
            insert(NodeAssociation).values(
                [
                    {
                        "id": association.id,
                        "group_id": association.group_id,
                        "node_id": association.node_id,
                        "created_at": association.created_at,
                        "updated_at": association.updated_at,
                    }
                    for association in node_association
                ]
            )
        )
