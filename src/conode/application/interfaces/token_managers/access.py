from typing import NamedTuple, Protocol, TypedDict

from conode.domain.user import User, UserSystemRole


class UserMeta(TypedDict):
    system_role: UserSystemRole
    email: str


class AccessTokenManagerResponse(NamedTuple):
    token: str
    expires_in: int


class AccessTokenManager(Protocol):
    def decode(self, token: str) -> UserMeta: ...
    def encode(self, user: User) -> AccessTokenManagerResponse: ...
