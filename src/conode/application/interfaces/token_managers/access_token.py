from typing import Protocol, TypedDict

from conode.domain.user import User, UserId


class UserMeta(TypedDict):
    user_id: UserId


class AccessTokenManager(Protocol):
    def encode(self, user: User) -> tuple[str, int]: ...
    def decode(self, token: str) -> UserMeta: ...
