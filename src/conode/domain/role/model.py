from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from typing import Final, NewType
from uuid import UUID

from conode.domain.company import Company, CompanyId
from conode.domain.role.errors import InvalidRoleNameFormatError
from conode.domain.shared import Entity, ValueObject

RoleId = NewType("RoleId", UUID)
RolePermissionId = NewType("RolePermissionId", UUID)

MIN_ALLOWED_ROLE_NAME_LENGTH: Final = 1
MAX_ALLOWED_ROLE_NAME_LENGTH: Final = 50


class PermissionType(StrEnum):
    VIEW = "VIEW"
    MODIFY = "MODIFY"


class RoleName(ValueObject[str]):
    def __init__(self, value: str) -> None:
        value = value.strip()

        if MIN_ALLOWED_ROLE_NAME_LENGTH <= len(value) <= MAX_ALLOWED_ROLE_NAME_LENGTH:
            raise InvalidRoleNameFormatError(
                "Company name must be between"
                f"{MIN_ALLOWED_ROLE_NAME_LENGTH} and "
                f"{MAX_ALLOWED_ROLE_NAME_LENGTH}",
                {"key": "name", "value": value},
            )

        super().__init__(value)


@dataclass
class Role(Entity[RoleId]):
    owner_company_id: CompanyId
    name: RoleName

    @classmethod
    def new(cls, id: RoleId, name: str, owner: Company) -> "Role":
        now = datetime.now(UTC)
        return Role(
            id=id,
            owner_company_id=owner.id,
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

    @classmethod
    def new(
        cls, id: RolePermissionId, role: Role, permission: PermissionType
    ) -> "RolePermission":
        now = datetime.now(UTC)
        return RolePermission(
            id=id,
            role_id=role.id,
            permission=permission,
            created_at=now,
            updated_at=now,
        )
