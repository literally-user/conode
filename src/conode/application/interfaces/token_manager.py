from typing import Protocol, TypedDict
from uuid import UUID

from conode.domain.user import UserSystemRole


class UserData(TypedDict):
    uuid: UUID
    role: UserSystemRole


class TokenManager(Protocol):
    def encode(self, user_id: UUID, user_role: UserSystemRole) -> str: ...
    def decode(self, token: str) -> UserData: ...
