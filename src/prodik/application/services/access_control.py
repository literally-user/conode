from dataclasses import dataclass

from prodik.application.errors import SessionExpiredError
from prodik.application.interfaces.token_managers import UserMeta
from prodik.domain.user import User


@dataclass
class AccessControlService:
    def ensure_revision_is_valid(self, meta: UserMeta, user: User) -> None:
        if meta["revision"] != user.token_revision:
            raise SessionExpiredError("Session has expired", None)
