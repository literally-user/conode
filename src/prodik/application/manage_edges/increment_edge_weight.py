from dataclasses import dataclass

from prodik.application.errors import (
    CompanyNotFoundError,
    EdgeNotFoundError,
    UserNotFoundError,
)
from prodik.application.interfaces.identity_provider import IdentityProvider
from prodik.application.interfaces.repositories import (
    CompanyRepository,
    EdgeRepository,
    UserRepository,
)
from prodik.application.interfaces.transaction_manager import TransactionManager
from prodik.application.services import AccessControlService
from prodik.domain.edge import EdgeId


@dataclass
class IncrementEdgeWeightInteractor:
    identity_provider: IdentityProvider
    company_repository: CompanyRepository
    edge_repository: EdgeRepository
    user_repository: UserRepository
    transaction_manager: TransactionManager
    access_control_service: AccessControlService

    async def execute(self, edge_id: EdgeId) -> None:
        async with self.transaction_manager:
            user_meta = self.identity_provider.get_current_user_meta()

            user = await self.user_repository.get_by_id(user_meta["user_id"])
            if user is None:
                raise UserNotFoundError("User not found", None)

            self.access_control_service.ensure_revision_is_valid(user_meta, user)

            company = await self.company_repository.get_by_user_id(user.id)
            if company is None:
                raise CompanyNotFoundError("Company not found", None)

            edge = await self.edge_repository.get_by_id(edge_id)
            if edge is None:
                raise EdgeNotFoundError("Edge not found", None)

            self.access_control_service.ensure_user_can_manipulate_edge(
                user,
                company,
                edge,
            )

            edge.increment_weight()

            await self.edge_repository.update(edge)
