from dataclasses import dataclass

from prodik.application.interfaces.repositories import (
    ContextRepository,
    EdgeRepository,
    NodeRepository,
)
from prodik.application.services import AccessControlService
from prodik.domain.context import ContextId
from prodik.domain.edge import Edge
from prodik.domain.node import Node, NodeId


@dataclass(frozen=True, slots=True, kw_only=True)
class GetNodeNeighboursRequestDTO:
    node_id: NodeId
    context_id: ContextId


@dataclass
class GetNodeNeighboursInteractor:
    access_control_service: AccessControlService
    node_repository: NodeRepository
    context_repository: ContextRepository
    edge_repository: EdgeRepository

    async def execute(
        self, request: GetNodeNeighboursRequestDTO
    ) -> list[tuple[Node, Edge]]:
        user = await self.access_control_service.get_authorized_user()

        context = await self.context_repository.get_by_id(request.context_id)

        await self.access_control_service.ensure_user_can_view_context(user, context)

        node = await self.node_repository.get_by_id(request.node_id)
        neighbour_edges = await self.edge_repository.get_neighbours_by_node_id(node.id)

        target_nodes_ids = []
        for edge in neighbour_edges:
            if edge.node_a_id == node.id:
                target_nodes_ids.append(edge.node_b_id)
                continue

            target_nodes_ids.append(edge.node_a_id)

        neighbour_nodes = await self.node_repository.get_all_by_ids(target_nodes_ids)

        return list(zip(neighbour_nodes, neighbour_edges, strict=True))
