from dataclasses import dataclass

import structlog
from sqlalchemy import delete, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from prodik.application.interfaces.repositories import RoleRepository
from prodik.domain.role import Role
from prodik.domain.role.model import RoleId, RoleName

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

    async def get_all_by_ids(self, roles_ids: list[RoleId]) -> list[Role]:
        logger.info(
            "Repository get roles by roles id",
            request_count=len(roles_ids),
        )
        if not roles_ids:
            return []

        result = await self.session.execute(select(Role).where(Role.id.in_(roles_ids)))  # type: ignore
        roles = list(result.scalars().all())
        logger.info(
            "Repository fetched roles by role id",
            found_count=len(roles),
        )

        return roles

    async def get_by_name(self, name: RoleName) -> Role | None:
        logger.info("Repository get role by name", role_name=name)
        result = await self.session.execute(
            select(Role).where(
                Role.name == name  # type: ignore
            )
        )

        role = result.scalar_one_or_none()
        logger.info("Repository fetched role by name", found=role is not None)

        return role

    async def update(self, role: Role) -> None:
        logger.info("Repository update role", role_id=role.id)
        await self.session.execute(
            update(Role)
            .where(
                Role.id == role.id  # type: ignore
            )
            .values(
                name=role.name,
            )
        )

    async def delete(self, role: Role) -> None:
        logger.info("Repository delete role", role_id=role.id)
        await self.session.execute(
            delete(Role).where(
                Role.id == role.id  # type: ignore
            )
        )

    async def get_by_id(self, role_id: RoleId) -> Role | None:
        logger.info("Repository get role by id", role_id=role_id)
        result = await self.session.execute(
            select(Role).where(Role.id == role_id)  # type: ignore
        )

        role = result.scalar_one_or_none()
        logger.info("Repository fetched role by id", found=role is not None)
        return role
