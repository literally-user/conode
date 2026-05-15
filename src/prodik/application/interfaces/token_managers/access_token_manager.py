from typing import NamedTuple, Protocol, TypedDict

from prodik.domain.user import User, UserId, UserSystemRole


class UserMeta(TypedDict):
    system_role: UserSystemRole
    user_id: UserId
    revision: int


class AccessTokenManagerResponse(NamedTuple):
    token: str
    expires_in: int


class AccessTokenManager(Protocol):
    def encode(self, user: User) -> AccessTokenManagerResponse: ...
    def decode(self, token: str) -> UserMeta: ...
