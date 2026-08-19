from sqlalchemy.orm import registry

from conode.domain.auth import Authorization, Session
from conode.domain.company import Company
from conode.domain.context import Context
from conode.domain.contract import Contract
from conode.domain.edge import Edge
from conode.domain.grant import UserGrant
from conode.domain.group import Group
from conode.domain.node import Node, NodeAssociation
from conode.domain.offer import Offer, OfferContext, OfferGroup, OfferLink
from conode.domain.role import Role, RolePermission
from conode.domain.user import User
from conode.infrastructure.persistence.schemas import (
    authorization_record_table,
    company_record_table,
    context_record_table,
    contract_record_table,
    edge_record_table,
    group_record_table,
    metadata,
    node_association_record_table,
    node_record_table,
    offer_context_record_table,
    offer_group_record_table,
    offer_link_record_table,
    offer_record_table,
    permission_record_table,
    role_record_table,
    session_record_table,
    user_grant_record_table,
    user_record_table,
)

registry_mapper = registry(metadata=metadata)


def start_mapper() -> None:
    registry_mapper.map_imperatively(User, user_record_table)
    registry_mapper.map_imperatively(Company, company_record_table)
    registry_mapper.map_imperatively(Node, node_record_table)
    registry_mapper.map_imperatively(Group, group_record_table)
    registry_mapper.map_imperatively(NodeAssociation, node_association_record_table)
    registry_mapper.map_imperatively(Context, context_record_table)
    registry_mapper.map_imperatively(Role, role_record_table)
    registry_mapper.map_imperatively(UserGrant, user_grant_record_table)
    registry_mapper.map_imperatively(RolePermission, permission_record_table)
    registry_mapper.map_imperatively(
        Edge,
        edge_record_table,
    )
    registry_mapper.map_imperatively(Offer, offer_record_table)
    registry_mapper.map_imperatively(OfferContext, offer_context_record_table)
    registry_mapper.map_imperatively(OfferGroup, offer_group_record_table)
    registry_mapper.map_imperatively(OfferLink, offer_link_record_table)
    registry_mapper.map_imperatively(Contract, contract_record_table)
    registry_mapper.map_imperatively(Session, session_record_table)
    registry_mapper.map_imperatively(Authorization, authorization_record_table)
