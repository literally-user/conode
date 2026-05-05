from dataclasses import dataclass

from conode.application.authorization.errors import InvalidTokenError
from conode.domain.authorization import Session


@dataclass
class AccessService:
    def verify_session(self, session: Session, token: str) -> None:
        if not session.token == token:
            raise InvalidTokenError(
                "Invalid refresh token", [{"key": "token", "value": token}]
            )
