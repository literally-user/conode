from sqlalchemy import (
    UUID,
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    MetaData,
    String,
    Table,
)
from sqlalchemy.orm import registry

from prodik.domain.authorization import LocalAuthorization, Session
from prodik.domain.company import Company
from prodik.domain.user import User, UserSystemRole
from prodik.infrastructure.persistence.types import (
    BioType,
    CompanyDescriptionType,
    CompanyNameType,
    EmailType,
    FirstNameType,
    LastNameType,
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
    Column("user_id", ForeignKey("user_record.id"), nullable=False),
    Column("host", String, nullable=False),
    Column("token", String, nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False),
    Column("updated_at", DateTime(timezone=True), nullable=False),
)

local_authorization_record_table = Table(
    "local_authorization_record",
    metadata,
    Column("id", UUID, primary_key=True, nullable=False),
    Column("user_id", ForeignKey("user_record.id"), nullable=False),
    Column("password", String, nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False),
    Column("updated_at", DateTime(timezone=True), nullable=False),
)

company_record_table = Table(
    "company_record",
    metadata,
    Column("id", UUID, primary_key=True, nullable=False),
    Column("owner_id", ForeignKey("user_record.id"), nullable=False),
    Column("name", CompanyNameType, nullable=False),
    Column("description", CompanyDescriptionType, nullable=False),
    Column("verified", Boolean, nullable=False),
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
