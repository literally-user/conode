from dataclasses import dataclass

from prodik.application.authorization.errors import InvalidTokenError
from prodik.application.services.errors import SessionExpiredError
from prodik.domain.authorization import Session
from prodik.domain.user import User


@dataclass
class AccessService:
    def verify_token(self, session: Session, token: str) -> None:
        if session.token != token:
            raise InvalidTokenError(
                "Invalid refresh token", [{"key": "token", "value": token}]
            )

    def ensure_session_active(self, session: Session, user: User) -> None:
        if session.token_revision != user.token_revision:
            raise SessionExpiredError("Session was expired", None)
