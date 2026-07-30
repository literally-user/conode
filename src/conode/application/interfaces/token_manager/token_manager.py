from typing import NamedTuple, Protocol, TypedDict

from conode.domain.user import User, UserSystemRole


class UserMeta(TypedDict):
    system_role: UserSystemRole
    first_name: str
    last_name: str
    email: str
    username: str


class TokenManagerResponse(NamedTuple):
    token: str
    expires_in: int


class TokenManager(Protocol):
    def decode(self, token: str) -> UserMeta: ...
    def encode(self, user: User) -> str: ...
