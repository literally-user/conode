from typing import Protocol

from prodik.application.interfaces.token_managers import UserMeta


class IdentityProvider(Protocol):
    def get_current_ip(self) -> str: ...
    def get_current_user_meta(self) -> UserMeta: ...
