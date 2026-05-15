from typing import Annotated

from polyfactory.factories.pydantic_factory import ModelFactory
from pydantic import BaseModel, Field

from prodik.domain.company import CompanyId
from prodik.domain.role import (
    EntityType,
    PermissionType,
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


class CreateRoleRequestFactory(ModelFactory[CreateRoleRequest]):
    __model__ = CreateRoleRequest


class UpdatePermissionRequestFactory(ModelFactory[UpdatePermissionRequest]):
    __model__ = UpdatePermissionRequest


class UpdateRoleRequestFactory(ModelFactory[UpdateRoleRequest]):
    __model__ = UpdateRoleRequest
