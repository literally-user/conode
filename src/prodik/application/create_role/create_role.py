from dataclasses import dataclass
from uuid import uuid4

from prodik.application.errors import CompanyNotFoundError, RoleAlreadyExistsError
from prodik.application.interfaces.repositories import (
    CompanyRepository,
    RolePermissionsRepository,
    RoleRepository,
)
from prodik.application.interfaces.transaction_manager import TransactionManager
from prodik.application.services import AccessControlService
from prodik.domain.company import CompanyId
from prodik.domain.role import (
    EntityType,
    PermissionType,
    Role,
    RoleId,
    RoleName,
    RolePermission,
    RolePermissionEntityId,
    RolePermissionId,
)


@dataclass(slots=True, frozen=True, kw_only=True)
class CreatePermissionRequestDTO:
    permission: PermissionType
    entity_type: EntityType
    entity_id: RolePermissionEntityId


@dataclass(slots=True, frozen=True, kw_only=True)
class CreateRoleRequestDTO:
    name: str
    permissions: list[CreatePermissionRequestDTO]
    company_id: CompanyId


@dataclass
class CreateRoleInteractor:
    role_repository: RoleRepository
    company_repository: CompanyRepository
    transaction_manager: TransactionManager
    access_control_service: AccessControlService
    role_permissions_repository: RolePermissionsRepository

    async def execute(self, request: CreateRoleRequestDTO) -> Role:
        async with self.transaction_manager:
            user = await self.access_control_service.get_authorized_user()

            company = await self.company_repository.get_by_id(request.company_id)
            if company is None:
                raise CompanyNotFoundError("Company not found", None)

            await self.access_control_service.ensure_user_can_create_roles(
                user, company
            )

            role = await self.role_repository.get_by_name(RoleName(request.name))
            if role is not None:
                raise RoleAlreadyExistsError(
                    "Role with this name already exists",
                    [{"key": "name", "value": request.name}],
                )

            role = Role.new(
                id=RoleId(uuid4()),
                name=request.name,
                company=company,
            )

            permissions = [
                RolePermission.new(
                    id=RolePermissionId(uuid4()),
                    role=role,
                    permission=permission.permission,
                    entity_type=permission.entity_type,
                    entity_id=permission.entity_id,
                )
                for permission in request.permissions
            ]

            await self.role_repository.create(role)
            await self.role_permissions_repository.create_all(permissions)

            return role
