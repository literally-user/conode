from dataclasses import dataclass

from sqlalchemy import insert, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from prodik.application.interfaces.repositories import UserRepository
from prodik.domain.user import Email, User, UserId, Username


@dataclass
class UserRepositoryImpl(UserRepository):
    session: AsyncSession

    async def create(self, user: User) -> None:
        await self.session.execute(
            insert(User).values(
                id=user.id,
                system_role=user.system_role,
                first_name=user.first_name,
                last_name=user.last_name,
                username=user.username,
                email=user.email,
                bio=user.bio,
                token_revision=user.token_revision,
                created_at=user.created_at,
                updated_at=user.updated_at,
            )
        )

    async def update(self, user: User) -> None:
        await self.session.execute(
            update(User)
            .where(
                User.id == user.id  # type: ignore
            )
            .values(
                system_role=user.system_role,
                first_name=user.first_name,
                last_name=user.last_name,
                username=user.username,
                email=user.email,
                bio=user.bio,
                token_revision=user.token_revision,
            )
        )

    async def get_by_username_or_email(
        self, username: Username, email: Email
    ) -> User | None:
        result = await self.session.execute(
            select(User)
            .where(
                or_(
                    User.username == username,  # type: ignore
                    User.email == email,  # type: ignore
                )
            )
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def get_by_id(self, id: UserId) -> User | None:
        result = await self.session.execute(
            select(User).where(User.id == id)  # type: ignore
        )

        return result.scalar_one_or_none()

    async def get_by_email(self, email: Email) -> User | None:
        result = await self.session.execute(
            select(User).where(User.email == email)  # type: ignore
        )

        return result.scalar_one_or_none()
