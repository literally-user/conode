import secrets
from dataclasses import dataclass

from prodik.application.interfaces.token_managers import RefreshTokenManager


@dataclass
class RefreshTokenManagerImpl(RefreshTokenManager):
    def encode(self) -> str:
        return secrets.token_urlsafe(64)
