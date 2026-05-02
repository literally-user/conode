from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Final, NewType
from uuid import UUID

from conode.domain.company.errors import (
    InvalidCompanyDescriptionFormatError,
    InvalidCompanyNameFormatError,
)
from conode.domain.role import Role, RoleId
from conode.domain.shared import Entity, ValueObject

CompanyId = NewType("CompanyId", UUID)
CompanyGrantId = NewType("CompanyGrantId", UUID)

MIN_ALLOWED_COMPANY_NAME_LENGTH: Final = 1
MAX_ALLOWED_COMPANY_NAME_LENGTH: Final = 50
MIN_ALLOWED_COMPANY_DESCRIPTION_LENGTH: Final = 20
MAX_ALLOWED_COMPANY_DESCRIPTION_LENGTH: Final = 300


class CompanyName(ValueObject[str]):
    def __init__(self, value: str) -> None:
        value = value.strip()

        if (
            MIN_ALLOWED_COMPANY_NAME_LENGTH
            <= len(value)
            <= MAX_ALLOWED_COMPANY_NAME_LENGTH
        ):
            raise InvalidCompanyNameFormatError(
                "Company name must be between"
                f"{MIN_ALLOWED_COMPANY_NAME_LENGTH} and "
                f"{MAX_ALLOWED_COMPANY_NAME_LENGTH}",
                {"key": "name", "value": value},
            )

        super().__init__(value)


class CompanyDescription(ValueObject[str]):
    def __init__(self, value: str) -> None:
        if (
            MAX_ALLOWED_COMPANY_DESCRIPTION_LENGTH
            <= len(value)
            <= MIN_ALLOWED_COMPANY_DESCRIPTION_LENGTH
        ):
            raise InvalidCompanyDescriptionFormatError(
                "Company description must be between"
                f"{MIN_ALLOWED_COMPANY_DESCRIPTION_LENGTH} and "
                f"{MAX_ALLOWED_COMPANY_DESCRIPTION_LENGTH}",
                {"key": "name", "value": value},
            )

        super().__init__(value)


@dataclass
class Company(Entity[CompanyId]):
    name: CompanyName
    description: CompanyDescription
    verified: bool

    @classmethod
    def new(cls, id: CompanyId, name: str, description: str) -> "Company":
        now = datetime.now(UTC)
        return Company(
            id=id,
            name=CompanyName(name),
            description=CompanyDescription(description),
            verified=False,
            created_at=now,
            updated_at=now,
        )

    def verify(self) -> None:
        self.verified = True
        self.touch()


@dataclass
class CompanyGrant(Entity[CompanyGrantId]):
    company_id: CompanyId
    role_id: RoleId

    @classmethod
    def new(cls, id: CompanyGrantId, role: Role, company: Company) -> "CompanyGrant":
        now = datetime.now(UTC)
        return CompanyGrant(
            id=id,
            company_id=company.id,
            role_id=role.id,
            created_at=now,
            updated_at=now,
        )
