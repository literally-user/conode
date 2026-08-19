from dataclasses import dataclass

import structlog
from sqlalchemy import and_, delete, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from conode.application.errors import RoleNotFoundError
from conode.application.interfaces.repositories import RoleRepository
from conode.domain.company import CompanyId
from conode.domain.grant import UserGrant
from conode.domain.role import Role, RoleId, RoleName
from conode.domain.user import UserId

logger = structlog.get_logger()


@dataclass
class RoleRepositoryImpl(RoleRepository):
    session: AsyncSession

    async def create(self, role: Role) -> None:
        logger.debug("Repository create role", role_id=role.id)
        await self.session.execute(
            insert(Role).values(
                id=role.id,
                name=role.name,
                owner_company_id=role.owner_company_id,
                created_at=role.created_at,
                updated_at=role.updated_at,
            ),
        )

    async def get_all_by_ids(self, roles_ids: list[RoleId]) -> list[Role]:
        logger.debug(
            "Repository get roles by ids",
            request_count=len(roles_ids),
        )
        if not roles_ids:
            return []

        result = await self.session.execute(select(Role).where(Role.id.in_(roles_ids)))  # type: ignore
        roles = list(result.scalars().all())
        logger.debug(
            "Repository fetched roles by ids",
            found_count=len(roles),
        )

        return roles

    async def get_all_by_user_id(self, user_id: UserId) -> list[Role]:
        logger.debug("Repository get roles by user id", user_id=user_id)
        result = await self.session.execute(
            select(Role)
            .join(UserGrant, UserGrant.role_id == Role.id)  # type: ignore
            .where(UserGrant.user_id == user_id)  # type: ignore
        )

        result_roles = list(result.scalars().all())
        logger.debug(
            "Repository fetched roles by user id",
            found_count=len(result_roles),
        )

        return result_roles

    async def update(self, role: Role) -> None:
        logger.debug("Repository update role", role_id=role.id)
        await self.session.execute(
            update(Role)
            .where(
                Role.id == role.id,  # type: ignore
            )
            .values(
                name=role.name,
            ),
        )

    async def delete(self, role: Role) -> None:
        logger.debug("Repository delete role", role_id=role.id)
        await self.session.execute(
            delete(Role).where(
                Role.id == role.id,  # type: ignore
            ),
        )

    async def get_by_id(self, role_id: RoleId) -> Role:
        logger.debug("Repository get role by id", role_id=role_id)
        result = await self.session.execute(
            select(Role).where(Role.id == role_id),  # type: ignore
        )

        role = result.scalar_one_or_none()

        logger.debug("Repository fetched role by id", found=role is not None)

        if role is None:
            raise RoleNotFoundError(
                "Role not found",
                [{"key": "role_id", "value": role_id}],
            )

        return role

    async def get_by_name_and_company_id(
        self, name: RoleName, company_id: CompanyId
    ) -> Role | None:
        logger.debug(
            "Repository get role by name and company id",
            company_id=company_id,
            name=name,
        )
        result = await self.session.execute(
            select(Role).where(
                and_(
                    Role.owner_company_id == company_id,  # type: ignore
                    Role.name == name,  # type: ignore
                )
            ),
        )

        role = result.scalar_one_or_none()
        logger.debug(
            "Repository fetched role by name and company id", found=role is not None
        )
        return role
