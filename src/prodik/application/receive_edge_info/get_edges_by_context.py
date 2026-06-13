from dataclasses import dataclass

from prodik.application.interfaces.repositories import (
    CompanyRepository,
    ContextRepository,
    EdgeRepository,
    NodeRepository,
)
from prodik.application.services import AccessControlService
from prodik.domain.context import ContextId
from prodik.domain.edge import Edge


@dataclass
class GetEdgesByContextInteractor:
    edge_repository: EdgeRepository
    access_control_service: AccessControlService
    company_repository: CompanyRepository
    context_repository: ContextRepository
    node_repository: NodeRepository

    async def execute(self, context_id: ContextId) -> list[Edge]:
        user = await self.access_control_service.get_authorized_user()

        context = await self.context_repository.get_by_id(context_id)

        await self.access_control_service.ensure_user_can_view_context(
            user,
            context,
        )

        return await self.edge_repository.get_all_by_context_id(context_id)
