from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Final, NewType
from uuid import UUID

from conode.domain.company import Company, CompanyId
from conode.domain.node.errors import (
    InvalidNodeDescriptionFormatError,
    InvalidNodeNameFormatError,
)
from conode.domain.shared import Entity, ValueObject

NodeId = NewType("NodeId", UUID)

MIN_ALLOWED_NODE_NAME_LENGTH: Final = 1
MAX_ALLOWED_NODE_NAME_LENGTH: Final = 50
MAX_ALLOWED_NODE_DESCRIPTION_LENGTH: Final = 300


class NodeName(ValueObject[str]):
    def __init__(self, value: str) -> None:
        value = value.strip()

        if MIN_ALLOWED_NODE_NAME_LENGTH <= len(value) <= MAX_ALLOWED_NODE_NAME_LENGTH:
            raise InvalidNodeNameFormatError(
                "Node name must be between"
                f"{MIN_ALLOWED_NODE_NAME_LENGTH} and "
                f"{MAX_ALLOWED_NODE_NAME_LENGTH}",
                {"key": "name", "value": value},
            )

        super().__init__(value)


class NodeDescription(ValueObject[str]):
    def __init__(self, value: str) -> None:
        if len(value) >= MAX_ALLOWED_NODE_DESCRIPTION_LENGTH:
            raise InvalidNodeDescriptionFormatError(
                "Node description must be shorter than "
                f"{MAX_ALLOWED_NODE_DESCRIPTION_LENGTH}",
                {"key": "name", "value": value},
            )

        super().__init__(value)


@dataclass
class Node(Entity[NodeId]):
    name: NodeName
    description: NodeDescription
    company_id: CompanyId

    @classmethod
    def new(cls, id: NodeId, name: str, description: str, company: Company) -> "Node":
        now = datetime.now(UTC)
        return Node(
            id=id,
            name=NodeName(name),
            description=NodeDescription(description),
            company_id=company.id,
            created_at=now,
            updated_at=now,
        )
