from dataclasses import dataclass

import structlog
from sqlalchemy import delete, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from prodik.application.interfaces.repositories import (
    NodeAssociationRepository,
    NodeRepository,
)
from prodik.domain.group import GroupId
from prodik.domain.node import Node, NodeAssociation, NodeAssociationId, NodeId

logger = structlog.get_logger()


@dataclass
class NodeRepositoryImpl(NodeRepository):
    session: AsyncSession

    async def create(self, node: Node) -> None:
        logger.info("Repository create node", node_id=node.id)
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
            logger.info("Repository get nodes by ids", ids_count=0)
            return []

        logger.info("Repository get nodes by ids", ids_count=len(nodes))
        result = await self.session.execute(
            select(Node).where(
                Node.id.in_(nodes)  # type: ignore
            )
        )

        result_nodes = list(result.scalars().all())
        logger.info("Repository fetched nodes by ids", found_count=len(result_nodes))
        return result_nodes

    async def delete(self, node: Node) -> None:
        logger.info("Repository delete node", node_id=node.id)
        await self.session.execute(
            delete(Node).where(
                Node.id == node.id  # type: ignore
            )
        )

    async def get_by_id(self, id: NodeId) -> Node | None:
        logger.info("Repository get node by id", node_id=id)
        result = await self.session.execute(
            select(Node).where(
                Node.id == id  # type: ignore
            )
        )

        node = result.scalar_one_or_none()
        logger.info("Repository fetched node by id", node_id=id, found=node is not None)
        return node

    async def update(self, node: Node) -> None:
        logger.info("Repository update node", node_id=node.id)
        await self.session.execute(
            update(Node)
            .where(
                Node.id == node.id  # type: ignore
            )
            .values(
                name=node.name,
                description=node.description,
            )
        )

    async def get_all_by_associations(self, nodes: list[NodeAssociation]) -> list[Node]:
        if not nodes:
            logger.info("Repository get nodes by associations", associations_count=0)
            return []

        node_ids = [association.node_id for association in nodes]
        logger.info(
            "Repository get nodes by associations",
            associations_count=len(nodes),
            node_ids_count=len(node_ids),
        )
        result = await self.session.execute(
            select(Node).where(
                Node.id.in_(node_ids)  # type: ignore
            )
        )

        result_nodes = list(result.scalars().all())
        logger.info(
            "Repository fetched nodes by associations", found_count=len(result_nodes)
        )
        return result_nodes


@dataclass
class NodeAssociationRepositoryImpl(NodeAssociationRepository):
    session: AsyncSession

    async def create(self, node_association: NodeAssociation) -> None:
        logger.info(
            "Repository create node association", association_id=node_association.id
        )
        await self.session.execute(
            insert(NodeAssociation).values(
                id=node_association.id,
                group_id=node_association.group_id,
                node_id=node_association.node_id,
                company_id=node_association.company_id,
                created_at=node_association.created_at,
                updated_at=node_association.updated_at,
            )
        )

    async def delete(self, node_association: NodeAssociation) -> None:
        logger.info(
            "Repository delete node association", association_id=node_association.id
        )
        await self.session.execute(
            delete(NodeAssociation).where(
                NodeAssociation.id == node_association.id  # type: ignore
            )
        )

    async def get_by_id(self, id: NodeAssociationId) -> NodeAssociation | None:
        logger.info("Repository get node association by id", association_id=id)
        result = await self.session.execute(
            select(NodeAssociation).where(
                NodeAssociation.id == id  # type: ignore
            )
        )

        association = result.scalar_one_or_none()
        logger.info(
            "Repository fetched node association by id",
            association_id=id,
            found=association is not None,
        )
        return association

    async def create_all(self, node_association: list[NodeAssociation]) -> None:
        if not node_association:
            logger.info("Repository create node associations batch", count=0)
            return

        logger.info(
            "Repository create node associations batch", count=len(node_association)
        )
        await self.session.execute(
            insert(NodeAssociation).values(
                [
                    {
                        "id": association.id,
                        "group_id": association.group_id,
                        "node_id": association.node_id,
                        "company_id": association.company_id,
                        "created_at": association.created_at,
                        "updated_at": association.updated_at,
                    }
                    for association in node_association
                ]
            )
        )

    async def get_all_by_group_id(self, group_id: GroupId) -> list[NodeAssociation]:
        logger.info("Repository get node associations by group id", group_id=group_id)
        result = await self.session.execute(
            select(NodeAssociation).where(
                NodeAssociation.group_id == group_id  # type: ignore
            )
        )

        associations = list(result.scalars())
        logger.info(
            "Repository fetched node associations by group id",
            group_id=group_id,
            count=len(associations),
        )
        return associations
