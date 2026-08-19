from dataclasses import dataclass

from conode.application.errors import (
    GroupNotFoundError,
)
from conode.application.interfaces.repositories import (
    CompanyRepository,
    GroupRepository,
    NodeAssociationRepository,
    NodeRepository,
)
from conode.application.interfaces.transaction_manager import TransactionManager
from conode.application.services import AccessControlService, AuthorizationService
from conode.domain.node import NodeAssociationId


@dataclass
class DetachNodeInteractor:
    node_repository: NodeRepository
    node_association_repository: NodeAssociationRepository
    access_control_service: AccessControlService
    authorization_service: AuthorizationService
    transaction_manager: TransactionManager
    group_repository: GroupRepository
    company_repository: CompanyRepository

    async def execute(self, association_id: NodeAssociationId) -> None:
        async with self.transaction_manager:
            user = await self.authorization_service.get_authorized_user()
            association = await self.node_association_repository.get_by_id(
                association_id,
            )

            group = await self.group_repository.get_by_id(association.group_id)
            if group is None:
                raise GroupNotFoundError(
                    "Group not found",
                    [{"key": "group_id", "value": association.group_id}],
                )

            await self.access_control_service.ensure_user_can_manipulate_group(
                user,
                group,
            )

            await self.node_association_repository.delete(association)
