from dataclasses import dataclass

from conode.application.interfaces.repositories import (
    CompanyRepository,
    ContextRepository,
    EdgeRepository,
)
from conode.application.interfaces.transaction_manager import TransactionManager
from conode.application.services import AccessControlService
from conode.domain.edge import EdgeId


@dataclass
class DeleteEdgeInteractor:
    company_repository: CompanyRepository
    edge_repository: EdgeRepository
    transaction_manager: TransactionManager
    access_control_service: AccessControlService
    context_repository: ContextRepository

    async def execute(self, edge_id: EdgeId) -> None:
        async with self.transaction_manager:
            user = await self.access_control_service.get_authorized_user()
            edge = await self.edge_repository.get_by_id(edge_id)
            context = await self.context_repository.get_by_id(edge.context_id)

            await self.access_control_service.ensure_user_can_manipulate_context(
                user,
                context,
            )

            await self.edge_repository.delete(edge)
