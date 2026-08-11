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
class DecrementEdgeWeightInteractor:
    company_repository: CompanyRepository
    edge_repository: EdgeRepository
    context_repository: ContextRepository
    transaction_manager: TransactionManager
    access_control_service: AccessControlService

    async def execute(self, edge_id: EdgeId) -> None:
        user = await self.access_control_service.get_authorized_user()

        async with self.transaction_manager:
            edge = await self.edge_repository.get_by_id(edge_id)
            context = await self.context_repository.get_by_id(edge.context_id)

            await self.access_control_service.ensure_user_can_manipulate_context(
                user,
                context,
            )

            edge.decrement_weight()

            await self.edge_repository.update(edge)
