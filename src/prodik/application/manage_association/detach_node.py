from dataclasses import dataclass

import structlog

from prodik.application.errors import (
    AssociationNotFoundError,
    UserNotFoundError,
)
from prodik.application.interfaces.identity_provider import IdentityProvider
from prodik.application.interfaces.repositories import (
    NodeAssociationRepository,
    UserRepository,
)
from prodik.application.interfaces.transaction_manager import TransactionManager
from prodik.application.services import AccessControlService
from prodik.domain.node import NodeAssociationId

logger = structlog.get_logger()


@dataclass
class DetachNodeInteractor:
    node_association_repository: NodeAssociationRepository
    access_control_service: AccessControlService
    transaction_manager: TransactionManager
    identity_provider: IdentityProvider
    user_repository: UserRepository

    async def execute(self, association_id: NodeAssociationId) -> None:
        async with self.transaction_manager:
            user_meta = self.identity_provider.get_current_user_meta()

            logger.info("Received user meta")

            user = await self.user_repository.get_by_id(user_meta["user_id"])
            if user is None:
                raise UserNotFoundError("User not found", None)

            self.access_control_service.ensure_revision_is_valid(user_meta, user)

            association = await self.node_association_repository.get_by_id(
                association_id
            )
            if association is None:
                raise AssociationNotFoundError("Association not found error", None)

            await self.node_association_repository.delete(association)

            return
