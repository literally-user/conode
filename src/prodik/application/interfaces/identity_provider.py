from typing import Protocol

from prodik.domain.user import UserId


class IdentityProvider(Protocol):
    def get_current_ip(self) -> str: ...
    def get_current_user_id(self) -> UserId: ...
