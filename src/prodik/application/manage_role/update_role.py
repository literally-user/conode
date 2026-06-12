from dataclasses import dataclass

from prodik.application.errors import RoleNotFoundError
from prodik.application.interfaces.repositories import (
    RolePermissionsRepository,
    RoleRepository,
)
from prodik.application.interfaces.transaction_manager import TransactionManager
from prodik.application.services import AccessControlService
from prodik.domain.role import (
    EntityType,
    PermissionType,
    Role,
    RoleId,
    RolePermission,
    RolePermissionEntityId,
    RolePermissionId,
)


@dataclass(slots=True, frozen=True, kw_only=True)
class UpdatePermissionRequestDTO:
    permission: PermissionType
    entity_type: EntityType
    entity_id: RolePermissionEntityId


@dataclass(slots=True, frozen=True, kw_only=True)
class UpdateRoleRequestDTO:
    name: str
    role_id: RoleId
    permissions: dict[RolePermissionId, UpdatePermissionRequestDTO]


@dataclass(slots=True, frozen=True, kw_only=True)
class UpdateRoleResponseDTO:
    role: Role
    permissions: list[RolePermission]


@dataclass
class UpdateRoleInteractor:
    role_permissions_repository: RolePermissionsRepository
    access_control_service: AccessControlService
    transaction_manager: TransactionManager
    role_repository: RoleRepository

    async def execute(self, request: UpdateRoleRequestDTO) -> UpdateRoleResponseDTO:
        async with self.transaction_manager:
            user = await self.access_control_service.get_authorized_user()

            role = await self.role_repository.get_by_id(request.role_id)
            if role is None:
                raise RoleNotFoundError(
                    "Role not found",
                    [{"key": "role_id", "value": request.role_id}],
                )

            await self.access_control_service.ensure_user_can_manipulate_role(
                user,
                role,
            )

            existing_permissions = (
                await self.role_permissions_repository.get_all_by_ids(
                    list(request.permissions.keys()),
                )
            )

            role.change_name(request.name)
            for permission in existing_permissions:
                permission.change_permission_type(
                    request.permissions[permission.id].permission,
                )
                permission.change_entity_id(
                    request.permissions[permission.id].entity_id,
                )
                permission.change_entity_type(
                    request.permissions[permission.id].entity_type,
                )

            await self.role_repository.update(role)
            await self.role_permissions_repository.update_all(existing_permissions)

            return UpdateRoleResponseDTO(role=role, permissions=existing_permissions)
