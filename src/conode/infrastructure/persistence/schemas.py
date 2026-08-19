from sqlalchemy import (
    UUID,
    Boolean,
    Column,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    MetaData,
    String,
    Table,
    UniqueConstraint,
)

from conode.domain.contract import ContractStatus
from conode.domain.offer import OfferLinkStatus, OfferStatus
from conode.domain.role import EntityType, PermissionType
from conode.domain.user import UserSystemRole
from conode.infrastructure.persistence.types import (
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
    OfferDescriptionType,
    OfferTitleType,
    RoleNameType,
    UsernameType,
)

metadata = MetaData()

user_record_table = Table(
    "user_record",
    metadata,
    Column("id", UUID, primary_key=True, nullable=False),
    Column("system_role", Enum(UserSystemRole), nullable=False),
    Column("username", UsernameType, nullable=False),
    Column("last_name", LastNameType, nullable=False),
    Column("first_name", FirstNameType, nullable=False),
    Column("email_verified", Boolean, nullable=False),
    Column("email", EmailType, nullable=False),
    Column("bio", BioType, nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False),
    Column("updated_at", DateTime(timezone=True), nullable=False),
    UniqueConstraint("username", name="uq_user_record_username"),
    UniqueConstraint("email", name="uq_user_record_email"),
)

authorization_record_table = Table(
    "authorization_record",
    metadata,
    Column("id", UUID, primary_key=True, nullable=False),
    Column("user_id", ForeignKey("user_record.id", ondelete="CASCADE"), nullable=False),
    Column("hashed_password", String, nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False),
    Column("updated_at", DateTime(timezone=True), nullable=False),
)

session_record_table = Table(
    "session_record",
    metadata,
    Column("id", UUID, primary_key=True, nullable=False),
    Column("ip", String, primary_key=True, nullable=False),
    Column("user_id", ForeignKey("user_record.id", ondelete="CASCADE"), nullable=False),
    Column("refresh_token", String, nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False),
    Column("updated_at", DateTime(timezone=True), nullable=False),
    UniqueConstraint("user_id", "ip", name="uq_session_record_user_id_ip"),
)

company_record_table = Table(
    "company_record",
    metadata,
    Column("id", UUID, primary_key=True, nullable=False),
    Column(
        "owner_id",
        ForeignKey("user_record.id", ondelete="CASCADE"),
        nullable=False,
    ),
    Column("name", CompanyNameType, nullable=False, unique=True),
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
    Column(
        "parent_group_id",
        ForeignKey("group_record.id", ondelete="CASCADE"),
        nullable=True,
    ),
    Column("created_at", DateTime(timezone=True), nullable=False),
    Column("updated_at", DateTime(timezone=True), nullable=False),
)

node_association_record_table = Table(
    "node_association_record",
    metadata,
    Column("id", UUID, primary_key=True, nullable=False),
    Column(
        "group_id",
        ForeignKey("group_record.id", ondelete="CASCADE"),
        nullable=False,
    ),
    Column("node_id", ForeignKey("node_record.id", ondelete="CASCADE"), nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False),
    Column("updated_at", DateTime(timezone=True), nullable=False),
    UniqueConstraint(
        "group_id", "node_id", name="uq_node_association_record_group_id_node_id"
    ),
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
    UniqueConstraint(
        "context_id",
        "node_a_id",
        "node_b_id",
        name="uq_edge_record_node_a_id_node_b_id_context_id",
    ),
)

role_record_table = Table(
    "role_record",
    metadata,
    Column("id", UUID, primary_key=True, nullable=False),
    Column("name", RoleNameType, nullable=False),
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
    Column("permission", Enum(PermissionType), nullable=False),
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

offer_link_record_table = Table(
    "offer_link_record",
    metadata,
    Column("id", UUID, primary_key=True, nullable=False),
    Column(
        "request_offer_id",
        ForeignKey("offer_record.id", ondelete="CASCADE"),
        nullable=False,
    ),
    Column(
        "response_offer_id",
        ForeignKey("offer_record.id", ondelete="CASCADE"),
        nullable=False,
    ),
    Column("status", Enum(OfferLinkStatus), nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False),
    Column("updated_at", DateTime(timezone=True), nullable=False),
)

offer_group_record_table = Table(
    "offer_group_record",
    metadata,
    Column("id", UUID, primary_key=True, nullable=False),
    Column(
        "offer_id",
        ForeignKey("offer_record.id", ondelete="CASCADE"),
        nullable=False,
    ),
    Column(
        "group_id",
        ForeignKey("group_record.id", ondelete="CASCADE"),
        nullable=False,
    ),
    Column("permission_type", Enum(PermissionType), nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False),
    Column("updated_at", DateTime(timezone=True), nullable=False),
)

offer_context_record_table = Table(
    "offer_context_record",
    metadata,
    Column("id", UUID, primary_key=True, nullable=False),
    Column(
        "offer_id",
        ForeignKey("offer_record.id", ondelete="CASCADE"),
        nullable=False,
    ),
    Column(
        "context_id",
        ForeignKey("context_record.id", ondelete="CASCADE"),
        nullable=False,
    ),
    Column("permission_type", Enum(PermissionType), nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False),
    Column("updated_at", DateTime(timezone=True), nullable=False),
)


offer_record_table = Table(
    "offer_record",
    metadata,
    Column("id", UUID, primary_key=True, nullable=False),
    Column("title", OfferTitleType, nullable=False),
    Column("description", OfferDescriptionType, nullable=False),
    Column("status", Enum(OfferStatus), nullable=False),
    Column(
        "from_company_id",
        ForeignKey("company_record.id", ondelete="CASCADE"),
        nullable=True,
    ),
    Column(
        "to_company_id",
        ForeignKey("company_record.id", ondelete="CASCADE"),
        nullable=False,
    ),
    Column(
        "from_offer",
        ForeignKey("offer_record.id", ondelete="CASCADE"),
        nullable=True,
    ),
    Column("requires_counteroffer", Boolean, nullable=False),
    Column("expires_in", DateTime(timezone=True)),
    Column("created_at", DateTime(timezone=True), nullable=False),
    Column("updated_at", DateTime(timezone=True), nullable=False),
)

contract_record_table = Table(
    "contract_record",
    metadata,
    Column("id", UUID, primary_key=True, nullable=False),
    Column("status", Enum(ContractStatus), nullable=False),
    Column(
        "company_a_id",
        ForeignKey("company_record.id", ondelete="CASCADE"),
        nullable=False,
    ),
    Column(
        "company_b_id",
        ForeignKey("company_record.id", ondelete="CASCADE"),
        nullable=False,
    ),
    Column(
        "company_a_offer_id",
        ForeignKey("offer_record.id", ondelete="CASCADE"),
        nullable=False,
    ),
    Column(
        "company_b_offer_id",
        ForeignKey("offer_record.id", ondelete="CASCADE"),
        nullable=True,
    ),
    Column(
        "company_a_role_id",
        ForeignKey("role_record.id", ondelete="CASCADE"),
        nullable=False,
    ),
    Column(
        "company_b_role_id",
        ForeignKey("role_record.id", ondelete="CASCADE"),
        nullable=True,
    ),
    Column("expires_in", DateTime(timezone=True)),
    Column("created_at", DateTime(timezone=True), nullable=False),
    Column("updated_at", DateTime(timezone=True), nullable=False),
)
