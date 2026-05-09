from dataclasses import dataclass

from prodik.application.errors import NotEnoughRightsError, SessionExpiredError
from prodik.application.interfaces.token_managers import UserMeta
from prodik.domain.company import Company
from prodik.domain.context import Context
from prodik.domain.edge import Edge
from prodik.domain.node import Node, NodeAssociation
from prodik.domain.user import User


@dataclass
class AccessControlService:
    def ensure_revision_is_valid(self, meta: UserMeta, user: User) -> None:
        if meta["revision"] != user.token_revision:
            raise SessionExpiredError("Session has expired", None)

    def ensure_user_can_manipulate_node_association(
        self, executor: User, executor_company: Company, node: NodeAssociation
    ) -> None:
        if executor_company.id != node.company_id and not executor.is_admin():
            raise NotEnoughRightsError("Not enough rights to perform operation", None)

    def ensure_user_can_manipulate_node(
        self, executor: User, executor_company: Company, node: Node
    ) -> None:
        if executor_company.id != node.company_id and not executor.is_admin():
            raise NotEnoughRightsError("Not enough rights to perform operation", None)

    def ensure_user_can_manipulate_context(
        self, executor: User, executor_company: Company, context: Context
    ) -> None:
        if executor_company.id != context.company_id and not executor.is_admin():
            raise NotEnoughRightsError("Not enough rights to perform operation", None)

    def ensure_user_can_manipulate_edge(
        self, executor: User, executor_company: Company, edge: Edge
    ) -> None:
        if executor_company.id != edge.company_id and not executor.is_admin():
            raise NotEnoughRightsError("Not enough rights to perform operation", None)
