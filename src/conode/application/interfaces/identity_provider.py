from typing import Protocol


class IdentityProvider(Protocol):
    def get_current_ip(self) -> str: ...
