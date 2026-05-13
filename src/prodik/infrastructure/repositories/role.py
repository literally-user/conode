from dataclasses import dataclass

import structlog
from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from prodik.application.interfaces.repositories import RoleRepository
from prodik.domain.role import Role
from prodik.domain.role.model import RoleId

logger = structlog.get_logger()


@dataclass
class RoleRepositoryImpl(RoleRepository):
    session: AsyncSession

    async def create(self, role: Role) -> None:
        logger.info("Repository create role", role_id=role.id)
        await self.session.execute(
            insert(Role).values(
                id=role.id,
                name=role.name,
                owner_company_id=role.owner_company_id,
                created_at=role.created_at,
                updated_at=role.updated_at,
            )
        )

    async def get_all_by_ids(self, ids: list[RoleId]) -> list[Role]:
        logger.info(
            "Repository get roles by roles id",
            roles_id=ids,
        )
        if not ids:
            return []

        result = await self.session.execute(select(Role).where(Role.id.in_(ids)))  # type: ignore
        roles = list(result.scalars().all())
        logger.info(
            "Repository fetched roles by role id",
            roles_id=ids,
            count=len(roles),
        )

        return roles
