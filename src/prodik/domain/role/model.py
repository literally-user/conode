from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from typing import Final, NewType, Self
from uuid import UUID

from prodik.domain.company import Company, CompanyId
from prodik.domain.context import ContextId
from prodik.domain.group import GroupId
from prodik.domain.role.errors import InvalidRoleNameFormatError
from prodik.domain.shared import Entity, ValueObject

RoleId = NewType("RoleId", UUID)
RolePermissionId = NewType("RolePermissionId", UUID)

MIN_ALLOWED_ROLE_NAME_LENGTH: Final = 1
MAX_ALLOWED_ROLE_NAME_LENGTH: Final = 50

type RolePermissionEntityId = ContextId | CompanyId | GroupId


class EntityType(StrEnum):
    GROUP = "GROUP"
    CONTEXT = "CONTEXT"
    COMPANY = "COMPANY"


class PermissionType(StrEnum):
    READ = "READ"
    MODIFY = "MODIFY"


class RoleName(ValueObject[str]):
    def __init__(self, value: str) -> None:
        value = value.strip()

        if MAX_ALLOWED_ROLE_NAME_LENGTH <= len(value) <= MIN_ALLOWED_ROLE_NAME_LENGTH:
            raise InvalidRoleNameFormatError(
                "Role name must be between "
                f"{MIN_ALLOWED_ROLE_NAME_LENGTH} and "
                f"{MAX_ALLOWED_ROLE_NAME_LENGTH}",
                [{"key": "name", "value": value}],
            )

        super().__init__(value)


@dataclass
class Role(Entity[RoleId]):
    owner_company_id: CompanyId
    name: RoleName

    @classmethod
    def new(cls, role_id: RoleId, name: str, company: Company) -> Self:
        now = datetime.now(UTC)
        return cls(
            id=role_id,
            owner_company_id=company.id,
            name=RoleName(name),
            created_at=now,
            updated_at=now,
        )

    def change_name(self, name: str) -> None:
        self.name = RoleName(name)
        self.touch()


@dataclass
class RolePermission(Entity[RolePermissionId]):
    role_id: RoleId
    permission: PermissionType
    entity_type: EntityType
    entity_id: RolePermissionEntityId

    @classmethod
    def new(
        cls,
        role_permission_id: RolePermissionId,
        role: Role,
        permission: PermissionType,
        entity_type: EntityType,
        entity_id: RolePermissionEntityId,
    ) -> Self:
        now = datetime.now(UTC)
        return cls(
            id=role_permission_id,
            role_id=role.id,
            permission=permission,
            entity_type=entity_type,
            entity_id=entity_id,
            created_at=now,
            updated_at=now,
        )

    def change_permission_type(self, permission_type: PermissionType) -> None:
        self.permission = permission_type
        self.touch()

    def change_entity_type(self, entity_type: EntityType) -> None:
        self.entity_type = entity_type
        self.touch()

    def change_entity_id(self, entity_id: RolePermissionEntityId) -> None:
        self.entity_id = entity_id
        self.touch()
