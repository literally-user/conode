from dataclasses import dataclass
from uuid import uuid4

from prodik.application.interfaces.repositories import GroupRepository
from prodik.domain.company import Company
from prodik.domain.group import Group, GroupId
from tests.factories.common import generate_random_string
from tests.factories.models.company_factory import CompanyFactory


@dataclass(slots=True)
class GroupFactory:
    group_repository: GroupRepository
    company_factory: CompanyFactory

    async def create_group(
        self, company: Company | None = None, parent_group: Group | None = None
    ) -> Group:
        group = Group.new(
            id=GroupId(uuid4()),
            name=generate_random_string(10),
            description=generate_random_string(30),
            company=company or await self.company_factory.create_company(),
            parent_group=parent_group,
        )
        await self.group_repository.create(group)
        return group
