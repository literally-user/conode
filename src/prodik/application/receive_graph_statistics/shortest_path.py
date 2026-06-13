from dataclasses import dataclass

from prodik.domain.node import NodeId
from prodik.domain.context import ContextId
from prodik.domain.edge import Edge
from prodik.application.services import AccessControlService
from prodik.application.interfaces.repositories import ContextRepository, EdgeRepository

@dataclass(frozen=True, slots=True, kw_only=True)
class FindShortestPathRequest:
    node_a_id: NodeId
    node_b_id: NodeId
    context_id: ContextId

@dataclass
class FindShortestPathInteractor:
    access_control_service: AccessControlService
    context_repository: ContextRepository
    edge_repository: EdgeRepository

    async def execute(self, request: FindShortestPathRequest) -> list[Edge]:
        user = await self.access_control_service.get_authorized_user()

        context = await self.context_repository.get_by_id(request.context_id)

        await self.access_control_service.ensure_user_can_view_context(
            user,
            context
        )

        edges = await self.edge_repository.get_all_by_context_id(context.id)

        # ...

        return []