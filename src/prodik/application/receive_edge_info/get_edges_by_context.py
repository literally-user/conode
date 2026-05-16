from dataclasses import dataclass

from prodik.application.errors import ContextNotFoundError
from prodik.application.interfaces.repositories import (
    CompanyRepository,
    ContextRepository,
    EdgeRepository,
    NodeRepository,
)
from prodik.application.services import AccessControlService
from prodik.domain.context import ContextId
from prodik.domain.node import Node


@dataclass
class GetEdgesByContextInteractor:
    edge_repository: EdgeRepository
    access_control_service: AccessControlService
    company_repository: CompanyRepository
    context_repository: ContextRepository
    node_repository: NodeRepository

    async def execute(self, context_id: ContextId) -> list[Node]:
        user = await self.access_control_service.get_authorized_user()

        context = await self.context_repository.get_by_id(context_id)
        if context is None:
            raise ContextNotFoundError(
                "Context not found",
                [{"key": "context_id", "value": context_id}],
            )

        await self.access_control_service.ensure_user_can_view_context(
            user,
            context,
        )

        edges = await self.edge_repository.get_all_by_context_id(context_id)
        node_ids = list(
            {edge.node_a_id for edge in edges} | {edge.node_b_id for edge in edges},
        )

        return await self.node_repository.get_all_by_ids(node_ids)
