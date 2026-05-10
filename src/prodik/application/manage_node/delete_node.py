from dataclasses import dataclass

from prodik.application.errors import (
    CompanyNotFoundError,
    NodeNotFoundError,
    NotEnoughRightsError,
)
from prodik.application.interfaces.identity_provider import IdentityProvider
from prodik.application.interfaces.repositories import (
    CompanyRepository,
    NodeRepository,
    UserRepository,
)
from prodik.application.interfaces.transaction_manager import TransactionManager
from prodik.application.services import AccessControlService
from prodik.domain.node import NodeId


@dataclass
class DeleteNodeInteractor:
    identity_provider: IdentityProvider
    transaction_manager: TransactionManager
    node_repository: NodeRepository
    user_repository: UserRepository
    company_repository: CompanyRepository
    access_control_service: AccessControlService

    async def execute(self, node_id: NodeId) -> None:
        async with self.transaction_manager:
            user = await self.access_control_service.get_authorized_user()

            company = await self.company_repository.get_by_user_id(user.id)
            if company is None:
                raise CompanyNotFoundError("Company not found", None)

            node = await self.node_repository.get_by_id(node_id)
            if node is None:
                raise NodeNotFoundError("Node not found", None)

            if node.company_id != company.id and not user.is_admin():
                raise NotEnoughRightsError(
                    "Not enough rights to perform operation", None
                )

            await self.node_repository.delete(node)
