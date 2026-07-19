from dataclasses import dataclass

from conode.application.interfaces.repositories import (
    RolePermissionsRepository,
    RoleRepository,
)
from conode.application.interfaces.transaction_manager import TransactionManager
from conode.application.services import (
    RoleManagmentService,
    RoleManagmentServiceResponse,
)
from conode.domain.company import Company
from conode.domain.context import Context
from conode.domain.group import Group
from conode.domain.role import EntityType, PermissionType
from tests.factories.common import generate_random_string

entity_types_map = {
    Context: EntityType.CONTEXT,
    Company: EntityType.COMPANY,
    Group: EntityType.GROUP,
}


@dataclass
class RoleFactory:
    role_managment_service: RoleManagmentService
    role_permissions_repository: RolePermissionsRepository
    transaction_manager: TransactionManager
    role_repository: RoleRepository

    async def build(
        self,
        company: Company,
        entities_with_permissions: list[
            tuple[Context | Company | Group, PermissionType]
        ],
    ) -> RoleManagmentServiceResponse:
        async with self.transaction_manager:
            role_managment_service_request = [
                (entity.id, entity_types_map[type(entity)], permission)
                for entity, permission in entities_with_permissions
            ]

            role_managment_service_response = (
                self.role_managment_service.create_role_with_permissions(
                    generate_random_string(),
                    company=company,
                    request=role_managment_service_request,
                )
            )

            await self.role_permissions_repository.create_all(
                role_managment_service_response.permissions
            )
            await self.role_repository.create(role_managment_service_response.role)

            return role_managment_service_response
