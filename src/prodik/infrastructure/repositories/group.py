from dataclasses import dataclass

from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from prodik.application.interfaces.repositories import GroupRepository
from prodik.domain.group.model import Group, GroupId


@dataclass
class GroupRepositoryImpl(GroupRepository):
    session: AsyncSession

    async def create(self, group: Group) -> None:
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
        result = await self.session.execute(
            select(Group).where(
                Group.id == id  # type: ignore
            )
        )

        return result.scalar_one_or_none()
