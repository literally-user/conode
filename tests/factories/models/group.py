from dataclasses import dataclass
from uuid import uuid4

from prodik.application.interfaces.repositories import GroupRepository
from prodik.application.interfaces.transaction_manager import TransactionManager
from prodik.domain.company import Company
from prodik.domain.group import Group, GroupId
from tests.factories.common import generate_random_string


@dataclass
class GroupFactory:
    group_repository: GroupRepository
    transaction_manager: TransactionManager

    async def build(
        self, *, company: Company, parent_group: Group | None = None
    ) -> Group:
        async with self.transaction_manager:
            group = Group.new(
                group_id=GroupId(uuid4()),
                name=generate_random_string(),
                description=generate_random_string(),
                company=company,
                parent_group=parent_group,
            )

            await self.group_repository.create(group)

            return group
