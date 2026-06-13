from dataclasses import dataclass

import structlog
from sqlalchemy import insert, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from prodik.application.interfaces.repositories import UserRepository
from prodik.domain.user import Email, User, UserId, Username

logger = structlog.get_logger()


@dataclass
class UserRepositoryImpl(UserRepository):
    session: AsyncSession

    async def create(self, user: User) -> None:
        logger.info("Repository create user", user_id=user.id)
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
            ),
        )

    async def update(self, user: User) -> None:
        logger.info("Repository update user", user_id=user.id)
        await self.session.execute(
            update(User)
            .where(
                User.id == user.id,  # type: ignore
            )
            .values(
                system_role=user.system_role,
                first_name=user.first_name,
                last_name=user.last_name,
                username=user.username,
                email=user.email,
                bio=user.bio,
                token_revision=user.token_revision,
            ),
        )

    async def get_by_username_or_email(
        self,
        username: Username,
        email: Email,
    ) -> User | None:
        logger.info(
            "Repository get user by username or email",
            username=username,
            email=email,
        )
        result = await self.session.execute(
            select(User)
            .where(
                or_(
                    User.username == username,  # type: ignore
                    User.email == email,  # type: ignore
                ),
            )
            .limit(1),
        )
        user = result.scalar_one_or_none()
        logger.info(
            "Repository fetched user by username or email",
        )
        return user

    async def get_by_username(self, username: Username) -> User | None:
        logger.info(
            "Repository get user by username",
            username=username,
        )
        result = await self.session.execute(
            select(User).where(
                User.username == username,  # type: ignore
            ),
        )
        user = result.scalar_one_or_none()
        logger.info("Repository fetched user by username", found=user is not None)
        return user

    async def get_by_id(self, user_id: UserId) -> User | None:
        logger.info("Repository get user by id", user_id=user_id)
        result = await self.session.execute(
            select(User).where(User.id == user_id),  # type: ignore
        )

        user = result.scalar_one_or_none()
        logger.info("Repository fetched user by id", found=user is not None)
        return user

    async def get_by_email(self, email: Email) -> User | None:
        logger.info("Repository get user by email", email=email)
        result = await self.session.execute(
            select(User).where(User.email == email),  # type: ignore
        )

        user = result.scalar_one_or_none()
        logger.info("Repository fetched user by email", found=user is not None)
        return user
