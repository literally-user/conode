from dataclasses import dataclass

from prodik.application.interfaces.repositories import ContextRepository, EdgeRepository
from prodik.application.services import AccessControlService, GraphManagmentService
from prodik.domain.context import ContextId
from prodik.domain.edge import Edge
from prodik.domain.node import NodeId


@dataclass(frozen=True, slots=True, kw_only=True)
class FindShortestPathRequestDTO:
    from_node_id: NodeId
    to_node_id: NodeId
    context_id: ContextId


@dataclass
class FindShortestPathInteractor:
    access_control_service: AccessControlService
    graph_managment_service: GraphManagmentService
    context_repository: ContextRepository
    edge_repository: EdgeRepository

    async def execute(self, request: FindShortestPathRequestDTO) -> list[Edge]:
        if request.from_node_id == request.to_node_id:
            return []

        user = await self.access_control_service.get_authorized_user()
        context = await self.context_repository.get_by_id(request.context_id)

        await self.access_control_service.ensure_user_can_view_context(user, context)

        edges = await self.edge_repository.get_all_by_context_id(context.id)

        return self.graph_managment_service.find_shortest_path(
            edges,
            request.from_node_id,
            request.to_node_id,
        )
