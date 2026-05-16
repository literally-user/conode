from dataclasses import dataclass
from uuid import uuid4

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

type RoleManagmentServiceRequest = list[
    tuple[RolePermissionEntityId, EntityType, PermissionType]
]


@dataclass(slots=True, frozen=True, kw_only=True)
class RoleManagmentServiceResponse:
    permissions: list[RolePermission]
    role: Role


@dataclass
class RoleManagmentService:
    def create_role_with_permissions(
        self, name: str, company: Company, request: RoleManagmentServiceRequest
    ) -> RoleManagmentServiceResponse:
        role = Role.new(
            role_id=RoleId(uuid4()),
            company=company,
            name=name,
        )

        permissions = [
            RolePermission.new(
                role_permission_id=RolePermissionId(uuid4()),
                role=role,
                permission=permission[2],
                entity_type=permission[1],
                entity_id=permission[0],
            )
            for permission in request
        ]

        return RoleManagmentServiceResponse(
            permissions=permissions,
            role=role,
        )
