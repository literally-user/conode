from dataclasses import dataclass

import structlog
from sqlalchemy import delete, insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from prodik.application.interfaces.repositories import GroupRepository
from prodik.domain.company import CompanyId
from prodik.domain.group import Group, GroupId

logger = structlog.get_logger()


@dataclass
class GroupRepositoryImpl(GroupRepository):
    session: AsyncSession

    async def create(self, group: Group) -> None:
        logger.info("Repository create group", group_id=group.id)
        await self.session.execute(
            insert(Group).values(
                id=group.id,
                name=group.name,
                description=group.description,
                company_id=group.company_id,
                created_at=group.created_at,
                updated_at=group.updated_at,
            )
        )

    async def get_by_id(self, id: GroupId) -> Group | None:
        logger.info("Repository get group by id", group_id=id)
        result = await self.session.execute(
            select(Group).where(
                Group.id == id  # type: ignore
            )
        )

        group = result.scalar_one_or_none()
        logger.info(
            "Repository fetched group by id", group_id=id, found=group is not None
        )
        return group

    async def delete(self, group: Group) -> None:
        logger.info("Repository delete group", group_id=group.id)
        await self.session.execute(
            delete(Group).where(
                Group.id == group.id  # type: ignore
            )
        )

    async def get_all_by_company_id(self, company_id: CompanyId) -> list[Group]:
        logger.info("Repository get groups by company id", company_id=company_id)
        result = await self.session.execute(
            delete(Group).where(
                Group.company_id == company_id  # type: ignore
            )
        )

        return list(result.scalars())

    async def get_all_by_ids(self, ids: list[GroupId]) -> list[Group]:
        if not ids:
            return []

        result = await self.session.execute(select(Group).where(Group.id.in_(ids)))  # type: ignore

        return list(result.scalars().all())
