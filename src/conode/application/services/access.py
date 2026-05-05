from dataclasses import dataclass

from conode.application.authorization.errors import InvalidCredentialsError
from conode.domain.authorization import Session


@dataclass
class AccessService:
    def verify_session(self, session: Session, token: str) -> None:
        if not session.token == token:
            raise InvalidCredentialsError("Invalid email or password", None)
