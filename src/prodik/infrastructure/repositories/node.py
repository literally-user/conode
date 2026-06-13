from dataclasses import dataclass

import structlog
from sqlalchemy import delete, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from prodik.application.errors import AssociationNotFoundError, NodeNotFoundError
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
            ),
        )

    async def get_all_by_ids(self, nodes_ids: list[NodeId]) -> list[Node]:
        logger.info("Repository get nodes by ids", request_count=len(nodes_ids))
        if not nodes_ids:
            return []

        result = await self.session.execute(
            select(Node).where(
                Node.id.in_(nodes_ids),  # type: ignore
            ),
        )

        result_nodes = list(result.scalars().all())
        logger.info("Repository fetched nodes by ids", found_count=len(result_nodes))
        return result_nodes

    async def delete(self, node: Node) -> None:
        logger.info("Repository delete node", node_id=node.id)
        await self.session.execute(
            delete(Node).where(
                Node.id == node.id,  # type: ignore
            ),
        )

    async def get_by_id(self, node_id: NodeId) -> Node:
        logger.info("Repository get node by id", node_id=node_id)
        result = await self.session.execute(
            select(Node).where(
                Node.id == node_id,  # type: ignore
            ),
        )

        node = result.scalar_one_or_none()

        logger.info("Repository fetched node by id", found=node is not None)

        if node is None:
            raise NodeNotFoundError(
                "Node not found",
                [{"key": "node_id", "value": node_id}],
            )

        return node

    async def update(self, node: Node) -> None:
        logger.info("Repository update node", node_id=node.id)
        await self.session.execute(
            update(Node)
            .where(
                Node.id == node.id,  # type: ignore
            )
            .values(
                name=node.name,
                description=node.description,
            ),
        )

    async def get_all_by_associations(
        self, associations: list[NodeAssociation]
    ) -> list[Node]:
        logger.info(
            "Repository get nodes by associations",
            request_count=len(associations),
        )
        if not associations:
            return []

        node_ids = [association.node_id for association in associations]
        result = await self.session.execute(
            select(Node).where(
                Node.id.in_(node_ids),  # type: ignore
            ),
        )

        result_nodes = list(result.scalars().all())
        logger.info(
            "Repository fetched nodes by associations",
            found_count=len(result_nodes),
        )
        return result_nodes


@dataclass
class NodeAssociationRepositoryImpl(NodeAssociationRepository):
    session: AsyncSession

    async def create(self, node_association: NodeAssociation) -> None:
        logger.info(
            "Repository create node association",
            association_id=node_association.id,
        )
        await self.session.execute(
            insert(NodeAssociation).values(
                id=node_association.id,
                group_id=node_association.group_id,
                node_id=node_association.node_id,
                created_at=node_association.created_at,
                updated_at=node_association.updated_at,
            ),
        )

    async def delete(self, node_association: NodeAssociation) -> None:
        logger.info(
            "Repository delete node association",
            association_id=node_association.id,
        )
        await self.session.execute(
            delete(NodeAssociation).where(
                NodeAssociation.id == node_association.id,  # type: ignore
            ),
        )

    async def get_by_id(
        self,
        node_association_id: NodeAssociationId,
    ) -> NodeAssociation:
        logger.info(
            "Repository get node association by id",
            association_id=node_association_id,
        )
        result = await self.session.execute(
            select(NodeAssociation).where(
                NodeAssociation.id == node_association_id,  # type: ignore
            ),
        )

        association = result.scalar_one_or_none()

        logger.info(
            "Repository fetched node association by id",
            found=association is not None,
        )

        if association is None:
            raise AssociationNotFoundError(
                "Association not found error",
                [{"key": "node_association_id", "value": node_association_id}],
            )

        return association

    async def create_all(self, node_association: list[NodeAssociation]) -> None:
        logger.info(
            "Repository create node associations batch",
            request_count=len(node_association),
        )
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
                ],
            ),
        )

    async def get_all_by_group_id(self, group_id: GroupId) -> list[NodeAssociation]:
        logger.info("Repository get node associations by group id", group_id=group_id)
        result = await self.session.execute(
            select(NodeAssociation).where(
                NodeAssociation.group_id == group_id,  # type: ignore
            ),
        )

        result_associations = list(result.scalars())
        logger.info(
            "Repository fetched node associations by group id",
            count=len(result_associations),
        )
        return result_associations

    async def get_all_by_node_id(
        self,
        node_id: NodeId,
    ) -> list[NodeAssociation]:
        logger.info(
            "Repository get node associations by node id",
            node_id=node_id,
        )

        result = await self.session.execute(
            select(NodeAssociation).where(
                NodeAssociation.node_id == node_id,  # type: ignore
            ),
        )
        result_associations = list(result.scalars().all())

        logger.info(
            "Repository fetched all node associations by node id",
            found_count=len(result_associations),
        )

        return result_associations
