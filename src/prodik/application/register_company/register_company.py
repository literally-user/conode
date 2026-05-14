from dataclasses import dataclass
from uuid import uuid4

from prodik.application.errors import CompanyAlreadyExistsError
from prodik.application.interfaces.repositories import (
    CompanyRepository,
    RolePermissionsRepository,
    RoleRepository,
    UserGrantRepository,
)
from prodik.application.interfaces.transaction_manager import TransactionManager
from prodik.application.services import AccessControlService
from prodik.domain.company import Company, CompanyId, CompanyName
from prodik.domain.grant import UserGrant, UserGrantId
from prodik.domain.role import (
    EntityType,
    PermissionType,
    Role,
    RoleId,
    RolePermission,
    RolePermissionId,
)


@dataclass(frozen=True, slots=True, kw_only=True)
class RegisterCompanyRequestDTO:
    description: str
    name: str


@dataclass
class RegisterCompanyInteractor:
    company_repository: CompanyRepository
    transaction_manager: TransactionManager
    access_control_service: AccessControlService
    role_permissions_repository: RolePermissionsRepository
    user_grant_repository: UserGrantRepository
    role_repository: RoleRepository

    async def execute(self, request: RegisterCompanyRequestDTO) -> Company:
        async with self.transaction_manager:
            user = await self.access_control_service.get_authorized_user()

            company = await self.company_repository.get_by_name(
                CompanyName(request.name)
            )
            if company is not None:
                raise CompanyAlreadyExistsError(
                    "Company with this name already exists",
                    [{"key": "name", "value": request.name}],
                )

            company = await self.company_repository.get_by_user_id(user.id)
            if company is not None:
                raise CompanyAlreadyExistsError(
                    "User can only have one company",
                    [{"key": "name", "value": request.name}],
                )

            company = Company.new(
                id=CompanyId(uuid4()),
                name=request.name,
                description=request.description,
                owner=user,
            )

            role = Role.new(id=RoleId(uuid4()), name="owner", company=company)

            permissions = [
                RolePermission.new(
                    id=RolePermissionId(uuid4()),
                    role=role,
                    permission=PermissionType.READ,
                    entity_type=EntityType.COMPANY,
                    entity_id=company.id,
                ),
                RolePermission.new(
                    id=RolePermissionId(uuid4()),
                    role=role,
                    permission=PermissionType.MODIFY,
                    entity_type=EntityType.COMPANY,
                    entity_id=company.id,
                ),
            ]

            grant = UserGrant.new(
                id=UserGrantId(uuid4()),
                role=role,
                user=user,
            )

            await self.company_repository.create(company)
            await self.role_repository.create(role)
            await self.role_permissions_repository.create_all(permissions)
            await self.user_grant_repository.create(grant)

            return company
