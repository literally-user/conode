from dataclasses import dataclass

import structlog

from prodik.application.errors import (
    AssociationNotFoundError,
    CompanyNotFoundError,
    NodeMustHaveAtLeastOneAssociationError,
)
from prodik.application.interfaces.repositories import (
    CompanyRepository,
    NodeAssociationRepository,
    NodeRepository,
)
from prodik.application.interfaces.transaction_manager import TransactionManager
from prodik.application.services import AccessControlService
from prodik.domain.node import NodeAssociationId

logger = structlog.get_logger()


@dataclass
class DetachNodeInteractor:
    node_repository: NodeRepository
    node_association_repository: NodeAssociationRepository
    access_control_service: AccessControlService
    transaction_manager: TransactionManager
    company_repository: CompanyRepository

    async def execute(self, association_id: NodeAssociationId) -> None:
        async with self.transaction_manager:
            user = await self.access_control_service.get_authorized_user()

            company = await self.company_repository.get_by_user_id(user.id)
            if company is None:
                raise CompanyNotFoundError("Company not found", None)

            association = await self.node_association_repository.get_by_id(
                association_id
            )
            if association is None:
                raise AssociationNotFoundError("Association not found error", None)

            existing_node_association = (
                await self.node_association_repository.get_by_node_id(
                    association.node_id
                )
            )
            if existing_node_association is None:
                raise NodeMustHaveAtLeastOneAssociationError(
                    "Node must have at least one association", None
                )

            self.access_control_service.ensure_user_can_manipulate_node_association(
                user,
                company,
                association,
            )

            await self.node_association_repository.delete(association)
