from dataclasses import dataclass

from prodik.application.errors import CompanyNotFoundError, NodeNotFoundError
from prodik.application.interfaces.repositories import CompanyRepository, NodeRepository
from prodik.application.interfaces.transaction_manager import TransactionManager
from prodik.application.services import AccessControlService
from prodik.domain.node import Node, NodeId


@dataclass(frozen=True, slots=True, kw_only=True)
class UpdateNodeRequestDTO:
    name: str
    description: str
    node_id: NodeId


@dataclass
class UpdateNodeInteractor:
    access_control_service: AccessControlService
    node_repository: NodeRepository
    company_repository: CompanyRepository
    transaction_manager: TransactionManager

    async def execute(self, request: UpdateNodeRequestDTO) -> Node:
        async with self.transaction_manager:
            user = await self.access_control_service.get_authorized_user()

            company = await self.company_repository.get_by_user_id(user.id)
            if company is None:
                raise CompanyNotFoundError("Company not found", None)

            node = await self.node_repository.get_by_id(request.node_id)
            if node is None:
                raise NodeNotFoundError("Node not found", None)

            self.access_control_service.ensure_user_can_manipulate_node(
                user,
                company,
                node,
            )

            node.set_name(request.name)
            node.set_description(request.description)

            return node
