from dataclasses import dataclass

from prodik.application.errors import (
    CompanyNotFoundError,
    ContextNotFoundError,
    EdgeNotFoundError,
)
from prodik.application.interfaces.repositories import (
    CompanyRepository,
    ContextRepository,
    EdgeRepository,
)
from prodik.application.interfaces.transaction_manager import TransactionManager
from prodik.application.services import AccessControlService
from prodik.domain.edge import EdgeId


@dataclass
class DecrementEdgeWeightInteractor:
    company_repository: CompanyRepository
    edge_repository: EdgeRepository
    context_repository: ContextRepository
    transaction_manager: TransactionManager
    access_control_service: AccessControlService

    async def execute(self, edge_id: EdgeId) -> None:
        async with self.transaction_manager:
            user = await self.access_control_service.get_authorized_user()

            edge = await self.edge_repository.get_by_id(edge_id)
            if edge is None:
                raise EdgeNotFoundError(
                    "Edge not found", [{"key": "edge_id", "value": edge_id}]
                )

            context = await self.context_repository.get_by_id(edge.context_id)
            if context is None:
                raise ContextNotFoundError(
                    "Context not found",
                    [{"key": "context_id", "value": edge.context_id}],
                )

            company = await self.company_repository.get_by_id(edge.company_id)
            if company is None:
                raise CompanyNotFoundError(
                    "Company not found",
                    [{"key": "company_id", "value": edge.company_id}],
                )

            await self.access_control_service.ensure_user_can_manipulate_context(
                user,
                context,
            )

            edge.decrement_weight()

            await self.edge_repository.update(edge)
