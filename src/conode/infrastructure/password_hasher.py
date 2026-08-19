from dataclasses import dataclass

from argon2 import PasswordHasher as Argon2Hasher
from argon2.exceptions import Argon2Error, InvalidHashError

from conode.application.interfaces.password_hasher import PasswordHasher
from conode.domain.auth import HashedPassword


@dataclass
class PasswordHasherImpl(PasswordHasher):
    _hasher = Argon2Hasher()

    def hash(self, password: str) -> str:
        return self._hasher.hash(password)

    def verify(self, hashed_password: HashedPassword, password: str) -> bool:
        try:
            return self._hasher.verify(hashed_password.value, password)
        except (InvalidHashError, Argon2Error):
            return False
