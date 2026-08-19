from dataclasses import dataclass

import structlog
from sqlalchemy import delete, insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from conode.application.interfaces.repositories import UserGrantRepository
from conode.domain.company import Company
from conode.domain.grant import UserGrant
from conode.domain.role import OWNER_COMPANY_ROLE_NAME, Role, RoleId, RoleName
from conode.domain.user import User, UserId

logger = structlog.get_logger()


@dataclass
class UserGrantRepositoryImpl(UserGrantRepository):
    session: AsyncSession

    async def create(self, grant: UserGrant) -> None:
        logger.debug("Repository create user grant", grant_id=grant.id)
        await self.session.execute(
            insert(UserGrant).values(
                id=grant.id,
                user_id=grant.user_id,
                role_id=grant.role_id,
                created_at=grant.created_at,
                updated_at=grant.updated_at,
            ),
        )

    async def delete(self, grant: UserGrant) -> None:
        logger.debug("Repository delete grant", grant_id=grant.id)
        await self.session.execute(
            delete(UserGrant).where(
                UserGrant.id == grant.id,  # type: ignore
            ),
        )

    async def revoke_company_owner_role_from_user(
        self,
        user: User,
        company: Company,
    ) -> Role:
        logger.debug(
            "Repository revoke company owner role",
            user_id=user.id,
            company=company.id,
        )

        deleted_grant = (
            delete(UserGrant)  # type: ignore
            .where(
                UserGrant.user_id == user.id,  # type: ignore
                UserGrant.role_id.in_(  # type: ignore
                    select(Role.id).where(  # type: ignore
                        Role.owner_company_id == company.id,  # type: ignore
                        Role.name == RoleName(OWNER_COMPANY_ROLE_NAME),  # type: ignore
                    )
                ),
            )
            .returning(UserGrant.role_id)  # type: ignore
            .cte("deleted_grant")
        )

        result = await self.session.execute(
            select(Role).join(
                deleted_grant,
                deleted_grant.c.role_id == Role.id,  # type: ignore
            )
        )

        return result.scalar_one()

    async def get_all_by_user_id(self, user_id: UserId) -> list[UserGrant]:
        logger.debug("Repository get user grants by user id", user_id=user_id)
        result = await self.session.execute(
            select(UserGrant).where(
                UserGrant.user_id == user_id,  # type: ignore
            ),
        )
        result_grants = list(result.scalars().all())
        logger.debug(
            "Repository fetched grants by user id",
            found_count=len(result_grants),
        )

        return result_grants

    async def get_by_user_and_role_id(
        self,
        user_id: UserId,
        role_id: RoleId,
    ) -> UserGrant | None:
        logger.debug(
            "Repository get user grant by user and role id",
            user_id=user_id,
            role_id=role_id,
        )
        result = await self.session.execute(
            select(UserGrant).where(
                UserGrant.user_id == user_id,  # type: ignore
            ),
        )

        grant = result.scalar_one_or_none()
        logger.debug(
            "Repository fetched user grant by user and role id",
            found=grant is not None,
        )

        return grant
