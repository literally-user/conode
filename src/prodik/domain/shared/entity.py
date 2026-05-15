from dataclasses import dataclass
from datetime import UTC, datetime
from typing import cast, override
from uuid import UUID


@dataclass
class Entity[EntityId: UUID]:
    id: EntityId
    created_at: datetime
    updated_at: datetime

    def touch(self) -> None:
        now = datetime.now(tz=UTC)
        self.updated_at = now

    @override
    def __eq__(self, value: object) -> bool:
        if isinstance(value, Entity):
            return cast("bool", self.id == value.id)

        raise NotImplementedError

    @override
    def __hash__(self) -> int:
        return hash(self.id)
