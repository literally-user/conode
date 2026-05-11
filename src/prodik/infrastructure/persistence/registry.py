from sqlalchemy import (
    UUID,
    Boolean,
    Column,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    MetaData,
    String,
    Table,
)
from sqlalchemy.orm import registry

from prodik.domain.authorization import LocalAuthorization, Session
from prodik.domain.company import Company
from prodik.domain.context import Context
from prodik.domain.edge import Edge
from prodik.domain.group import Group
from prodik.domain.node import Node, NodeAssociation
from prodik.domain.role import EntityType, Role
from prodik.domain.user import User, UserSystemRole
from prodik.infrastructure.persistence.types import (
    BioType,
    CompanyDescriptionType,
    CompanyNameType,
    ContextDescriptionType,
    ContextNameType,
    EmailType,
    FirstNameType,
    GroupDescriptionType,
    GroupNameType,
    LastNameType,
    NodeDescriptionType,
    NodeNameType,
    UsernameType,
)

metadata = MetaData()
registry_mapper = registry(metadata=metadata)

user_record_table = Table(
    "user_record",
    metadata,
    Column("id", UUID, primary_key=True, nullable=False),
    Column("system_role", Enum(UserSystemRole), nullable=False),
    Column("username", UsernameType, nullable=False),
    Column("last_name", LastNameType, nullable=False),
    Column("first_name", FirstNameType, nullable=False),
    Column("email", EmailType, nullable=False),
    Column("bio", BioType, nullable=False),
    Column("token_revision", Integer, nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False),
    Column("updated_at", DateTime(timezone=True), nullable=False),
)

session_record_table = Table(
    "session_record",
    metadata,
    Column("id", UUID, primary_key=True, nullable=False),
    Column("user_id", ForeignKey("user_record.id", ondelete="CASCADE"), nullable=False),
    Column("host", String, nullable=False),
    Column("token", String, nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False),
    Column("updated_at", DateTime(timezone=True), nullable=False),
)

local_authorization_record_table = Table(
    "local_authorization_record",
    metadata,
    Column("id", UUID, primary_key=True, nullable=False),
    Column("user_id", ForeignKey("user_record.id", ondelete="CASCADE"), nullable=False),
    Column("password", String, nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False),
    Column("updated_at", DateTime(timezone=True), nullable=False),
)

company_record_table = Table(
    "company_record",
    metadata,
    Column("id", UUID, primary_key=True, nullable=False),
    Column(
        "owner_id", ForeignKey("user_record.id", ondelete="CASCADE"), nullable=False
    ),
    Column("name", CompanyNameType, nullable=False),
    Column("description", CompanyDescriptionType, nullable=False),
    Column("verified", Boolean, nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False),
    Column("updated_at", DateTime(timezone=True), nullable=False),
)

node_record_table = Table(
    "node_record",
    metadata,
    Column("id", UUID, primary_key=True, nullable=False),
    Column("name", NodeNameType, nullable=False),
    Column("description", NodeDescriptionType, nullable=False),
    Column(
        "company_id",
        ForeignKey("company_record.id", ondelete="CASCADE"),
        nullable=False,
    ),
    Column("created_at", DateTime(timezone=True), nullable=False),
    Column("updated_at", DateTime(timezone=True), nullable=False),
)

group_record_table = Table(
    "group_record",
    metadata,
    Column("id", UUID, primary_key=True, nullable=False),
    Column("name", GroupNameType, nullable=False),
    Column("description", GroupDescriptionType, nullable=False),
    Column(
        "company_id",
        ForeignKey("company_record.id", ondelete="CASCADE"),
        nullable=False,
    ),
    Column("created_at", DateTime(timezone=True), nullable=False),
    Column("updated_at", DateTime(timezone=True), nullable=False),
)

node_association_record_table = Table(
    "node_association_record",
    metadata,
    Column("id", UUID, primary_key=True, nullable=False),
    Column(
        "company_id",
        ForeignKey("company_record.id", ondelete="CASCADE"),
        nullable=False,
    ),
    Column(
        "group_id", ForeignKey("group_record.id", ondelete="CASCADE"), nullable=False
    ),
    Column("node_id", ForeignKey("node_record.id", ondelete="CASCADE"), nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False),
    Column("updated_at", DateTime(timezone=True), nullable=False),
)


context_record_table = Table(
    "context_record",
    metadata,
    Column("id", UUID, primary_key=True, nullable=False),
    Column(
        "company_id",
        ForeignKey("company_record.id", ondelete="CASCADE"),
        nullable=False,
    ),
    Column("name", ContextNameType, nullable=False),
    Column("description", ContextDescriptionType, nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False),
    Column("updated_at", DateTime(timezone=True), nullable=False),
)

edge_record_table = Table(
    "edge_record",
    metadata,
    Column("id", UUID, primary_key=True, nullable=False),
    Column(
        "node_a_id",
        ForeignKey("node_record.id", ondelete="CASCADE"),
        nullable=False,
    ),
    Column(
        "node_b_id",
        ForeignKey("node_record.id", ondelete="CASCADE"),
        nullable=False,
    ),
    Column(
        "context_id",
        ForeignKey("context_record.id", ondelete="CASCADE"),
        nullable=False,
    ),
    Column(
        "company_id",
        ForeignKey("company_record.id", ondelete="CASCADE"),
        nullable=False,
    ),
    Column("weight", Float, nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False),
    Column("updated_at", DateTime(timezone=True), nullable=False),
)

role_record_table = Table(
    "role_record",
    metadata,
    Column("id", UUID, primary_key=True, nullable=False),
    Column(
        "owner_company_id",
        ForeignKey("company_record.id", ondelete="CASCADE"),
        nullable=False,
    ),
    Column("created_at", DateTime(timezone=True), nullable=False),
    Column("updated_at", DateTime(timezone=True), nullable=False),
)

permission_record_table = Table(
    "permission_record",
    metadata,
    Column("id", UUID, primary_key=True, nullable=False),
    Column(
        "role_id",
        ForeignKey("role_record.id", ondelete="CASCADE"),
        nullable=False,
    ),
    Column(
        "owner_company_id",
        ForeignKey("company_record.id", ondelete="CASCADE"),
        nullable=False,
    ),
    Column("entity_id", UUID, nullable=False),
    Column("entity_type", Enum(EntityType), nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False),
    Column("updated_at", DateTime(timezone=True), nullable=False),
)

user_grant_record_table = Table(
    "user_grant_record",
    metadata,
    Column("id", UUID, primary_key=True, nullable=False),
    Column(
        "role_id",
        ForeignKey("role_record.id", ondelete="CASCADE"),
        nullable=False,
    ),
    Column(
        "user_id",
        ForeignKey("user_record.id", ondelete="CASCADE"),
        nullable=False,
    ),
    Column("created_at", DateTime(timezone=True), nullable=False),
    Column("updated_at", DateTime(timezone=True), nullable=False),
)

company_grant_record_table = Table(
    "company_grant_record",
    metadata,
    Column("id", UUID, primary_key=True, nullable=False),
    Column(
        "role_id",
        ForeignKey("role_record.id", ondelete="CASCADE"),
        nullable=False,
    ),
    Column(
        "company_id",
        ForeignKey("company_record.id", ondelete="CASCADE"),
        nullable=False,
    ),
    Column("created_at", DateTime(timezone=True), nullable=False),
    Column("updated_at", DateTime(timezone=True), nullable=False),
)


def start_mapper() -> None:
    registry_mapper.map_imperatively(User, user_record_table)
    registry_mapper.map_imperatively(Session, session_record_table)
    registry_mapper.map_imperatively(
        LocalAuthorization, local_authorization_record_table
    )
    registry_mapper.map_imperatively(Company, company_record_table)
    registry_mapper.map_imperatively(Node, node_record_table)
    registry_mapper.map_imperatively(Group, group_record_table)
    registry_mapper.map_imperatively(NodeAssociation, node_association_record_table)
    registry_mapper.map_imperatively(Context, context_record_table)
    registry_mapper.map_imperatively(Role, role_record_table)
    registry_mapper.map_imperatively(
        Edge,
        edge_record_table,
    )
