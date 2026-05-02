from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Final, NewType
from uuid import UUID

from conode.domain.company import Company, CompanyId
from conode.domain.group.error import (
    InvalidGroupDescriptionFormatError,
    InvalidGroupNameFormatError,
)
from conode.domain.shared import Entity, ValueObject

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
                {"key": "name", "value": value},
            )

        super().__init__(value)


class GroupDescription(ValueObject[str]):
    def __init__(self, value: str) -> None:
        if len(value) >= MAX_ALLOWED_GROUP_DESCRIPTION_LENGTH:
            raise InvalidGroupDescriptionFormatError(
                "Group description must be shorter than "
                f"{MAX_ALLOWED_GROUP_DESCRIPTION_LENGTH}",
                {"key": "name", "value": value},
            )

        super().__init__(value)


@dataclass
class Group(Entity[GroupId]):
    name: GroupName
    description: GroupDescription
    company_id: CompanyId

    @classmethod
    def new(cls, id: GroupId, name: str, description: str, company: Company) -> "Group":
        now = datetime.now(UTC)
        return Group(
            id=id,
            name=GroupName(name),
            description=GroupDescription(description),
            company_id=company.id,
            created_at=now,
            updated_at=now,
        )
