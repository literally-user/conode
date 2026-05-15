from dataclasses import dataclass
from uuid import uuid4

from prodik.application.interfaces.repositories import NodeRepository
from prodik.domain.company import Company
from prodik.domain.group import Group
from prodik.domain.node import Node, NodeAssociation, NodeId
from prodik.domain.user import User
from tests.factories.common import generate_random_string
from tests.factories.models.company_factory import CompanyFactory
from tests.factories.models.group_factory import GroupFactory
from tests.factories.models.node_association_factory import NodeAssociationFactory
from tests.factories.models.user_factory import UserFactory


@dataclass(slots=True)
class NodeFactory:
    group_factory: GroupFactory
    node_association_factory: NodeAssociationFactory
    node_repository: NodeRepository
    user_factory: UserFactory
    company_factory: CompanyFactory

    async def create_node(
        self,
        association: NodeAssociation | None = None,
        company: Company | None = None,
        group: Group | None = None,
        user: User | None = None,
    ) -> Node:
        if user is None:
            user = (await self.user_factory.create_user(admin=False)).user
        if company is None:
            company = await self.company_factory.create_company(user)

        node = Node.new(
            id=NodeId(uuid4()),
            name=generate_random_string(10),
            description=generate_random_string(30),
            company=company,
        )

        if group is None:
            group = await self.group_factory.create_group(company)

        await self.node_repository.create(node)

        if association is None:
            association = await self.node_association_factory.create_association(
                node, group
            )

        return node
