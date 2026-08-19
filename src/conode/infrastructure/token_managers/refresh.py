from dataclasses import dataclass
from secrets import token_urlsafe

from conode.application.interfaces.token_managers import RefreshTokenManager


@dataclass
class RefreshTokenManagerImpl(RefreshTokenManager):
    def encode(self) -> str:
        return token_urlsafe(32)
