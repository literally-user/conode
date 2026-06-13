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
from prodik.application.services import AccessControlService, RoleManagmentService
from prodik.domain.company import Company, CompanyId, CompanyName
from prodik.domain.grant import UserGrant, UserGrantId
from prodik.domain.role import (
    EntityType,
    PermissionType,
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
    role_managment_service: RoleManagmentService
    role_permissions_repository: RolePermissionsRepository
    user_grant_repository: UserGrantRepository
    role_repository: RoleRepository

    async def execute(self, request: RegisterCompanyRequestDTO) -> Company:
        async with self.transaction_manager:
            user = await self.access_control_service.get_authorized_user()

            company = await self.company_repository.get_by_name(
                CompanyName(request.name),
            )
            if company is not None:
                raise CompanyAlreadyExistsError(
                    "Company with this name already exists",
                    [{"key": "name", "value": request.name}],
                )

            company = Company.new(
                company_id=CompanyId(uuid4()),
                name=request.name,
                description=request.description,
                owner=user,
            )

            role_managment_service_response = (
                self.role_managment_service.create_role_with_permissions(
                    name="owner",
                    company=company,
                    request=[
                        (
                            company.id,
                            EntityType.COMPANY,
                            PermissionType.READ,
                        ),
                        (
                            company.id,
                            EntityType.COMPANY,
                            PermissionType.MODIFY,
                        ),
                    ],
                )
            )

            grant = UserGrant.new(
                user_grant_id=UserGrantId(uuid4()),
                role=role_managment_service_response.role,
                user=user,
            )

            await self.company_repository.create(company)
            await self.role_repository.create(role_managment_service_response.role)
            await self.role_permissions_repository.create_all(
                role_managment_service_response.permissions,
            )
            await self.user_grant_repository.create(grant)

            return company
