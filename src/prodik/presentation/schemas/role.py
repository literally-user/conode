from typing import Annotated

from pydantic import BaseModel, Field

from prodik.domain.company import CompanyId
from prodik.domain.role import (
    EntityType,
    PermissionType,
    RoleId,
    RolePermissionEntityId,
    RolePermissionId,
)
from prodik.domain.role.model import (
    MAX_ALLOWED_ROLE_NAME_LENGTH,
    MIN_ALLOWED_ROLE_NAME_LENGTH,
)


class CreatePermissionRequest(BaseModel):
    permission: PermissionType
    entity_type: EntityType
    entity_id: RolePermissionEntityId


class CreateRoleRequest(BaseModel):
    name: Annotated[
        str,
        Field(
            min_length=MIN_ALLOWED_ROLE_NAME_LENGTH,
            max_length=MAX_ALLOWED_ROLE_NAME_LENGTH,
        ),
    ]
    company_id: CompanyId
    permissions: list[CreatePermissionRequest]


class UpdatePermissionRequest(BaseModel):
    permission: PermissionType
    entity_type: EntityType
    entity_id: RolePermissionEntityId


class UpdateRoleRequest(BaseModel):
    name: str
    permissions: dict[RolePermissionId, UpdatePermissionRequest]


class RoleSchema(BaseModel):
    id: RoleId
    owner_company_id: CompanyId
    name: str


class PermissionSchema(BaseModel):
    id: RolePermissionId
    role_id: RoleId
    permission: PermissionType
    entity_type: EntityType
    entity_id: RolePermissionEntityId


class UpdateRoleResponse(BaseModel):
    role: RoleSchema
    permissions: list[PermissionSchema]
