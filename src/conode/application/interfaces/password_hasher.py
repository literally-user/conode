from typing import Protocol

from conode.domain.auth import HashedPassword


class PasswordHasher(Protocol):
    def hash(self, password: str) -> str: ...
    def verify(self, hashed_password: HashedPassword, password: str) -> bool: ...
