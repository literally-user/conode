from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Final, NewType
from uuid import UUID

from prodik.domain.company import Company, CompanyId
from prodik.domain.context.errors import (
    InvalidContextDescriptionFormatError,
    InvalidContextNameFormatError,
)
from prodik.domain.shared import Entity, ValueObject

ContextId = NewType("ContextId", UUID)

MIN_ALLOWED_CONTEXT_NAME_LENGTH: Final = 1
MAX_ALLOWED_CONTEXT_NAME_LENGTH: Final = 50
MAX_ALLOWED_CONTEXT_DESCRIPTION_LENGTH: Final = 300


class ContextName(ValueObject[str]):
    def __init__(self, value: str) -> None:
        value = value.strip()

        if not (
            MIN_ALLOWED_CONTEXT_NAME_LENGTH
            <= len(value)
            <= MAX_ALLOWED_CONTEXT_NAME_LENGTH
        ):
            raise InvalidContextNameFormatError(
                "Context name must be between"
                f"{MIN_ALLOWED_CONTEXT_NAME_LENGTH} and "
                f"{MAX_ALLOWED_CONTEXT_NAME_LENGTH}",
                [{"key": "name", "value": value}],
            )

        super().__init__(value)


class ContextDescription(ValueObject[str]):
    def __init__(self, value: str) -> None:
        if len(value) >= MAX_ALLOWED_CONTEXT_DESCRIPTION_LENGTH:
            raise InvalidContextDescriptionFormatError(
                "Context description must be shorter than "
                f"{MAX_ALLOWED_CONTEXT_DESCRIPTION_LENGTH}",
                [{"key": "description", "value": value}],
            )

        super().__init__(value)


@dataclass
class Context(Entity[ContextId]):
    name: ContextName
    description: ContextDescription
    company_id: CompanyId

    @classmethod
    def new(
        cls, id: ContextId, name: str, description: str, company: Company
    ) -> "Context":
        now = datetime.now(UTC)
        return Context(
            id=id,
            name=ContextName(name),
            description=ContextDescription(description),
            company_id=company.id,
            created_at=now,
            updated_at=now,
        )
