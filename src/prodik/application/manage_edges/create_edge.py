from dataclasses import dataclass
from typing import Final
from uuid import uuid4

from prodik.application.errors import (
    CompanyNotFoundError,
    ContextNotFoundError,
    NodeNotFoundError,
    UserNotFoundError,
)
from prodik.application.interfaces.identity_provider import IdentityProvider
from prodik.application.interfaces.repositories import (
    CompanyRepository,
    ContextRepository,
    EdgeRepository,
    NodeRepository,
    UserRepository,
)
from prodik.application.interfaces.transaction_manager import TransactionManager
from prodik.application.services import AccessControlService
from prodik.domain.context import ContextId
from prodik.domain.edge import Edge, EdgeId
from prodik.domain.node import NodeId

EXPECTED_COUNT_OF_NODES: Final = 2


@dataclass(frozen=True, slots=True, kw_only=True)
class CreateEdgeRequestDTO:
    node_a_id: NodeId
    node_b_id: NodeId
    context_id: ContextId


@dataclass
class CreateEdgeInteractor:
    access_control_service: AccessControlService
    transaction_manager: TransactionManager
    context_repository: ContextRepository
    company_repository: CompanyRepository
    identity_provider: IdentityProvider
    node_repository: NodeRepository
    user_repository: UserRepository
    edge_repository: EdgeRepository

    async def execute(self, request: CreateEdgeRequestDTO) -> Edge:
        async with self.transaction_manager:
            user_meta = self.identity_provider.get_current_user_meta()

            user = await self.user_repository.get_by_id(user_meta["user_id"])
            if user is None:
                raise UserNotFoundError("User not found", None)

            self.access_control_service.ensure_revision_is_valid(user_meta, user)

            company = await self.company_repository.get_by_user_id(user.id)
            if company is None:
                raise CompanyNotFoundError("Company not found", None)

            context = await self.context_repository.get_by_id(request.context_id)
            if context is None:
                raise ContextNotFoundError("Context not found", None)

            nodes = await self.node_repository.get_all_by_ids(
                [request.node_a_id, request.node_b_id]
            )
            if len(nodes) != EXPECTED_COUNT_OF_NODES:
                raise NodeNotFoundError(
                    "Some of nodes not found",
                    [
                        {"key": "node_a_id", "value": str(request.node_a_id)},
                        {"key": "node_b_id", "value": str(request.node_b_id)},
                    ],
                )

            edge = Edge.new(
                id=EdgeId(uuid4()),
                node_a=nodes[0],
                node_b=nodes[1],
                company=company,
                context=context,
                weight=0,
            )

            await self.edge_repository.create(edge)

            return edge
