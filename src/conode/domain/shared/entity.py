from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any, cast, override
from uuid import UUID


@dataclass
class Entity[EntityId: UUID]:
    id: EntityId
    created_at: datetime
    updated_at: datetime

    @override
    def __setattr__(self, name: str, value: Any) -> None:
        self.__dict__[name] = value
        self.__dict__["updated_at"] = datetime.now(UTC)

    @override
    def __eq__(self, value: object) -> bool:
        if isinstance(value, Entity):
            return cast("bool", self.id == value.id)

        raise NotImplementedError

    @override
    def __hash__(self) -> int:
        return hash(self.id)
