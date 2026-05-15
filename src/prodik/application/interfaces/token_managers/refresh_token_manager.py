from typing import Protocol


class RefreshTokenManager(Protocol):
    def encode(self) -> str: ...
