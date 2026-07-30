from dataclasses import dataclass
from uuid import uuid4

from conode.application.interfaces.repositories import (
    CompanyRepository,
    RolePermissionsRepository,
    RoleRepository,
    UserGrantRepository,
)
from conode.application.interfaces.transaction_manager import TransactionManager
from conode.application.services import RoleManagmentService
from conode.domain.company import Company, CompanyId
from conode.domain.grant import UserGrant, UserGrantId
from conode.domain.role import EntityType, PermissionType
from conode.domain.user import User
from tests.factories.common import generate_random_string


@dataclass
class CompanyFactory:
    role_permissions_repository: RolePermissionsRepository
    role_managment_service: RoleManagmentService
    user_grant_repository: UserGrantRepository
    transaction_manager: TransactionManager
    company_repository: CompanyRepository
    role_repository: RoleRepository

    async def build(self, *, owner: User) -> Company:
        async with self.transaction_manager:
            company = Company.new(
                company_id=CompanyId(uuid4()),
                name=generate_random_string(
                    include_special_symbols=False, include_digits=False
                ),
                description=generate_random_string(200),
                owner=owner,
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
                user=owner,
            )

            await self.company_repository.create(company)
            await self.role_repository.create(role_managment_service_response.role)
            await self.role_permissions_repository.create_all(
                role_managment_service_response.permissions
            )
            await self.user_grant_repository.create(grant)

            return company
