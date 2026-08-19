from collections import deque
from dataclasses import dataclass

from conode.application.errors import DepthCannotBeNegativeError
from conode.application.interfaces.repositories import (
    ContextRepository,
    EdgeRepository,
    NodeRepository,
)
from conode.application.services import AccessControlService, AuthorizationService
from conode.domain.context import ContextId
from conode.domain.edge import Edge
from conode.domain.node import Node, NodeId


@dataclass(frozen=True, slots=True, kw_only=True)
class GetNodeNeighboursRequestDTO:
    node_id: NodeId
    context_id: ContextId
    depth: int


@dataclass
class GetNodeNeighboursInteractor:
    access_control_service: AccessControlService
    authorization_service: AuthorizationService
    node_repository: NodeRepository
    context_repository: ContextRepository
    edge_repository: EdgeRepository

    async def execute(
        self, request: GetNodeNeighboursRequestDTO
    ) -> list[tuple[Node, Edge]]:
        user = await self.authorization_service.get_authorized_user()

        context = await self.context_repository.get_by_id(request.context_id)

        await self.access_control_service.ensure_user_can_view_context(user, context)

        node = await self.node_repository.get_by_id(request.node_id)
        edges = await self.edge_repository.get_all_by_context_id(context.id)

        if request.depth < 0:
            raise DepthCannotBeNegativeError(
                "Depth cannot be negative", [{"key": "depth", "value": request.depth}]
            )

        queue: deque[tuple[NodeId, int]] = deque([(node.id, 0)])
        neighbours: dict[NodeId, Edge] = {}

        while queue:
            node_id, depth = queue.popleft()

            if depth >= request.depth:
                continue

            for edge in edges:
                other = edge.other_end(node_id)

                if (
                    (node_id in {edge.node_a_id, edge.node_b_id})
                    and other not in neighbours
                    and other != node.id
                ):
                    neighbours[other] = edge
                    queue.append((other, depth + 1))

        neighbour_nodes = await self.node_repository.get_all_by_ids(
            list(neighbours.keys())
        )

        return [(node, neighbours[node.id]) for node in neighbour_nodes]
