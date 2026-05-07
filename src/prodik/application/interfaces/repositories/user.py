from typing import Protocol

from prodik.domain.user import Email, User, Username


class UserRepository(Protocol):
    async def create(self, user: User) -> None: ...
    async def get_by_username_or_email(
        self, username: Username, email: Email
    ) -> User | None: ...
