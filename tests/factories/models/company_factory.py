import asyncio
from dataclasses import dataclass
from uuid import uuid4

from prodik.application.interfaces.repositories import (
    CompanyRepository,
    RolePermissionsRepository,
    RoleRepository,
    UserGrantRepository,
)
from prodik.domain.company import Company, CompanyId
from prodik.domain.grant import UserGrant, UserGrantId
from prodik.domain.role import (
    EntityType,
    PermissionType,
    Role,
    RoleId,
    RolePermission,
    RolePermissionId,
)
from prodik.domain.user import User
from tests.factories.common import generate_random_string
from tests.factories.models.user_factory import UserFactory


@dataclass(slots=True)
class CompanyFactory:
    role_repository: RoleRepository
    role_permissions_repository: RolePermissionsRepository
    user_grant_repository: UserGrantRepository
    company_repository: CompanyRepository
    user_factory: UserFactory

    async def create_company(self, user: User | None = None) -> Company:
        if user is None:
            user = (await self.user_factory.create_user(admin=False)).user

        company = Company.new(
            id=CompanyId(uuid4()),
            name=generate_random_string(10),
            description=generate_random_string(300),
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
        await asyncio.gather(
            self.role_permissions_repository.create_all(permissions),
            self.user_grant_repository.create(grant),
        )

        return company
