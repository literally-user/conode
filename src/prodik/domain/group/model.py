from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Final, NewType
from uuid import UUID

from prodik.domain.company import Company, CompanyId
from prodik.domain.group.errors import (
    GroupCannotInheritedFromItselfError,
    InvalidGroupDescriptionFormatError,
    InvalidGroupNameFormatError,
)
from prodik.domain.shared import Entity, ValueObject

GroupId = NewType("GroupId", UUID)

MIN_ALLOWED_GROUP_NAME_LENGTH: Final = 1
MAX_ALLOWED_GROUP_NAME_LENGTH: Final = 50
MAX_ALLOWED_GROUP_DESCRIPTION_LENGTH: Final = 300


class GroupName(ValueObject[str]):
    def __init__(self, value: str) -> None:
        value = value.strip()

        if MIN_ALLOWED_GROUP_NAME_LENGTH <= len(value) <= MAX_ALLOWED_GROUP_NAME_LENGTH:
            raise InvalidGroupNameFormatError(
                "Group name must be between"
                f"{MIN_ALLOWED_GROUP_NAME_LENGTH} and "
                f"{MAX_ALLOWED_GROUP_NAME_LENGTH}",
                [{"key": "name", "value": value}],
            )

        super().__init__(value)


class GroupDescription(ValueObject[str]):
    def __init__(self, value: str) -> None:
        if len(value) >= MAX_ALLOWED_GROUP_DESCRIPTION_LENGTH:
            raise InvalidGroupDescriptionFormatError(
                "Group description must be shorter than "
                f"{MAX_ALLOWED_GROUP_DESCRIPTION_LENGTH}",
                [{"key": "description", "value": value}],
            )

        super().__init__(value)


@dataclass
class Group(Entity[GroupId]):
    name: GroupName
    description: GroupDescription
    company_id: CompanyId
    parent_group_id: GroupId | None

    @classmethod
    def new(
        cls,
        id: GroupId,
        name: str,
        description: str,
        company: Company,
        parent_group: "Group | None",
    ) -> "Group":
        if parent_group is not None and parent_group.id == id:
            raise GroupCannotInheritedFromItselfError(
                "Group cannot inherit from itself",
                [{"key": "parent_group", "value": parent_group}],
            )

        now = datetime.now(UTC)
        return Group(
            id=id,
            name=GroupName(name),
            description=GroupDescription(description),
            company_id=company.id,
            parent_group_id=parent_group.id if parent_group is not None else None,
            created_at=now,
            updated_at=now,
        )
