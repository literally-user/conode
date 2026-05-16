from dataclasses import dataclass
from typing import Final
from uuid import uuid4

from prodik.application.errors import (
    CompanyNotFoundError,
    ContextNotFoundError,
    EdgeAlreadyExistsError,
    NodeNotFoundError,
)
from prodik.application.interfaces.repositories import (
    CompanyRepository,
    ContextRepository,
    EdgeRepository,
    NodeRepository,
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
    node_repository: NodeRepository
    edge_repository: EdgeRepository

    async def execute(self, request: CreateEdgeRequestDTO) -> Edge:
        async with self.transaction_manager:
            user = await self.access_control_service.get_authorized_user()

            context = await self.context_repository.get_by_id(request.context_id)
            if context is None:
                raise ContextNotFoundError(
                    "Context not found",
                    [{"key": "context_id", "value": request.context_id}],
                )

            company = await self.company_repository.get_by_id(context.company_id)
            if company is None:
                raise CompanyNotFoundError(
                    "Company by context not found",
                    [{"key": "context_id", "value": request.context_id}],
                )

            await self.access_control_service.ensure_user_can_manipulate_context(
                user,
                context,
            )

            nodes = await self.node_repository.get_all_by_ids(
                [request.node_a_id, request.node_b_id]
            )
            if len(nodes) != EXPECTED_COUNT_OF_NODES:
                raise NodeNotFoundError(
                    "Some of nodes not found",
                    [
                        {"key": "node_a_id", "value": request.node_a_id},
                        {"key": "node_b_id", "value": request.node_b_id},
                    ],
                )

            edge = await self.edge_repository.get_by_nodes_and_context(
                node_a_id=request.node_a_id,
                node_b_id=request.node_b_id,
                context_id=request.context_id,
            )
            if edge is not None:
                raise EdgeAlreadyExistsError(
                    "Edge between nodes in this context already exists",
                    [
                        {"key": "node_a_id", "value": request.node_a_id},
                        {"key": "node_b_id", "value": request.node_b_id},
                        {"key": "context_id", "value": request.context_id},
                    ],
                )

            edge = Edge.new(
                edge_id=EdgeId(uuid4()),
                node_a=nodes[0],
                node_b=nodes[1],
                company=company,
                context=context,
                weight=0,
            )

            await self.edge_repository.create(edge)

            return edge
