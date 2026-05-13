from typing import Annotated

from pydantic import BaseModel, Field

from prodik.domain.company import CompanyId
from prodik.domain.role import (
    EntityType,
    PermissionType,
    RoleId,
    RolePermissionEntityId,
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


class RoleSchema(BaseModel):
    id: RoleId
    owner_company_id: CompanyId
    name: str
