from dataclasses import dataclass

from prodik.application.errors import CompanyNotFoundError, RoleAlreadyExistsError
from prodik.application.interfaces.repositories import (
    CompanyRepository,
    RolePermissionsRepository,
    RoleRepository,
)
from prodik.application.interfaces.transaction_manager import TransactionManager
from prodik.application.services import AccessControlService, RoleManagmentService
from prodik.domain.company import CompanyId
from prodik.domain.role import (
    EntityType,
    PermissionType,
    Role,
    RoleName,
    RolePermissionEntityId,
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
    role_managment_service: RoleManagmentService
    role_permissions_repository: RolePermissionsRepository

    async def execute(self, request: CreateRoleRequestDTO) -> Role:
        async with self.transaction_manager:
            user = await self.access_control_service.get_authorized_user()

            company = await self.company_repository.get_by_id(request.company_id)
            if company is None:
                raise CompanyNotFoundError(
                    "Company not found",
                    [{"key": "company_id", "value": request.company_id}],
                )

            await self.access_control_service.ensure_user_can_create_roles(
                user,
                company,
            )

            role = await self.role_repository.get_by_name_and_company_id(
                RoleName(request.name), company.id
            )
            if role is not None:
                raise RoleAlreadyExistsError(
                    "Role with this name already exists",
                    [{"key": "name", "value": request.name}],
                )

            role_managment_service_response = (
                self.role_managment_service.create_role_with_permissions(
                    name=request.name,
                    company=company,
                    request=[
                        (
                            permission.entity_id,
                            permission.entity_type,
                            permission.permission,
                        )
                        for permission in request.permissions
                    ],
                )
            )

            await self.role_repository.create(role_managment_service_response.role)
            await self.role_permissions_repository.create_all(
                role_managment_service_response.permissions
            )

            return role_managment_service_response.role
