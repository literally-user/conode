from dataclasses import dataclass

import structlog
from sqlalchemy import delete, insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from prodik.application.errors import GroupNotFoundError
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
            ),
        )

    async def get_by_id(self, group_id: GroupId) -> Group:
        logger.info("Repository get group by id", group_id=group_id)
        result = await self.session.execute(
            select(Group).where(
                Group.id == group_id,  # type: ignore
            ),
        )

        group = result.scalar_one_or_none()

        logger.info("Repository fetched group by id", found=group is not None)

        if group is None:
            raise GroupNotFoundError(
                "Group not found",
                [{"key": "group_id", "value": group_id}],
            )

        return group

    async def delete(self, group: Group) -> None:
        logger.info("Repository delete group", group_id=group.id)
        await self.session.execute(
            delete(Group).where(
                Group.id == group.id,  # type: ignore
            ),
        )

    async def get_all_by_company_id(self, company_id: CompanyId) -> list[Group]:
        logger.info("Repository get groups by company id", company_id=company_id)
        result = await self.session.execute(
            delete(Group).where(
                Group.company_id == company_id,  # type: ignore
            ),
        )

        result_groups = list(result.scalars())
        logger.info(
            "Repository fetched groups by company id",
            found_count=len(result_groups),
        )
        return result_groups

    async def get_all_by_ids(self, group_ids: list[GroupId]) -> list[Group]:
        logger.info("Repository get groups by ids", request_count=len(group_ids))
        if not group_ids:
            return []

        result = await self.session.execute(
            select(Group).where(Group.id.in_(group_ids)),  # type: ignore
        )

        result_groups = list(result.scalars().all())
        logger.info("Repository fetched groups by ids", found_count=len(result_groups))
        return result_groups
