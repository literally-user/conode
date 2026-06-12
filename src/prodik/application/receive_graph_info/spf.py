from dataclasses import dataclass
import asyncio

from prodik.application.services import AccessControlService
from prodik.application.interfaces.repositories import (
    ContextRepository,
    NodeRepository,
    EdgeRepository,
    GroupRepository,
)
from prodik.application.errors import (
    NodeNotFoundError,
    ContextNotFoundError,
    CannotFindShortestPathThroughSameNodeError,
    GroupNotFoundError,
)
from prodik.domain.node import NodeId
from prodik.domain.group import GroupId
from prodik.domain.edge import Edge
from prodik.domain.context import ContextId


@dataclass(frozen=True, slots=True, kw_only=True)
class FindShortestPathRequestDTO:
    context_id: ContextId
    node_a_id: NodeId
    node_b_id: NodeId
    node_a_group_id: GroupId
    node_b_group_id: GroupId


@dataclass
class FindShortestPathInteractor:
    access_control_service: AccessControlService
    node_repository: NodeRepository
    context_repository: ContextRepository
    edge_repository: EdgeRepository
    group_repository: GroupRepository

    async def execute(self, request: FindShortestPathRequestDTO) -> list[Edge]:
        user = await self.access_control_service.get_authorized_user()

        if request.node_a_id == request.node_b_id:
            raise CannotFindShortestPathThroughSameNodeError(
                "Cannot find shortest path through the same node",
                [
                    {"key": "node_a_id", "value": request.node_a_id},
                    {"key": "node_b_id", "value": request.node_b_id},
                ],
            )

        node_a, node_b = await self.node_repository.get_all_by_ids([
            request.node_a_id,
            request.node_b_id,
        ])

        if node_a is None or node_b is None:
            raise NodeNotFoundError(
                "Some of nodes not found",
                [
                    {"key": "node_a_id", "value": request.node_a_id},
                    {"key": "node_b_id", "value": request.node_b_id}
                ]
            )

        context = await self.context_repository.get_by_id(request.context_id)

        if context is None:
            raise ContextNotFoundError(
                "Context not found",
                [{"key": "context_id", "value": request.context_id}],
            )

        node_a_group, node_b_group = await self.group_repository.get_all_by_ids([
            request.node_a_group_id,
            request.node_b_group_id,
        ])

        if node_a_group is None or node_b_group is None:
            raise GroupNotFoundError(
                "Some of groups not found",
                [
                    {"key": "node_a_group_id", "value": request.node_a_group_id},
                    {"key": "node_b_group_id", "value": request.node_b_group_id}
                ],
            )

        await asyncio.gather(
            self.access_control_service.ensure_user_can_view_context(user, context),
            self.access_control_service.ensure_user_can_view_group(user, node_a_group),
            self.access_control_service.ensure_user_can_view_group(user, node_b_group),
        )

        edges = await self.edge_repository.get_all_connecting_edges_by_nodes(
            request.node_a_id,
            request.node_b_id,
        )

        return []