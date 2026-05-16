from dataclasses import dataclass
from uuid import uuid4

from prodik.application.interfaces.repositories import (
    RolePermissionsRepository,
    RoleRepository,
)
from prodik.domain.company import Company
from prodik.domain.role import (
    EntityType,
    PermissionType,
    Role,
    RoleId,
    RolePermission,
    RolePermissionEntityId,
    RolePermissionId,
)
from tests.factories.common import generate_random_string


@dataclass(slots=True)
class RoleFactory:
    role_repository: RoleRepository
    role_permissions_repository: RolePermissionsRepository

    async def create_role(
        self,
        *,
        company: Company,
        name: str | None = None,
        with_permissions: bool = True,
        permission_entity_id: RolePermissionEntityId | None = None,
    ) -> Role:

        role = Role.new(
            role_id=RoleId(uuid4()),
            name=name or generate_random_string(10),
            company=company,
        )

        permissions: list[RolePermission] = []

        if with_permissions:
            entity_id = permission_entity_id or company.id

            permissions = [
                RolePermission.new(
                    role_permission_id=RolePermissionId(uuid4()),
                    role=role,
                    permission=PermissionType.READ,
                    entity_type=EntityType.COMPANY,
                    entity_id=entity_id,
                ),
                RolePermission.new(
                    role_permission_id=RolePermissionId(uuid4()),
                    role=role,
                    permission=PermissionType.MODIFY,
                    entity_type=EntityType.COMPANY,
                    entity_id=entity_id,
                ),
            ]

        await self.role_repository.create(role)

        if permissions:
            await self.role_permissions_repository.create_all(permissions)

        return role
