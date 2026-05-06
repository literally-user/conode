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
    CompanyDescriptionType,
    CompanyNameType,
    EmailType,
    FirstNameType,
    LastNameType,
    UsernameType,
)

metadata = MetaData()
registry_mapper = registry(metadata=metadata)

user_profile_table = Table(
    "user_record",
    metadata,
    Column("id", UUID, nullable=False, primary_key=True),
    Column("token_revision", Integer, nullable=False),
    Column("system_role", Enum(UserSystemRole), nullable=False),
    Column("username", UsernameType, nullable=False),
    Column("first_name", FirstNameType, nullable=False),
    Column("last_name", LastNameType, nullable=True),
    Column("email", EmailType, nullable=False),
    Column("bio", String(3000), nullable=True),
    Column("updated_at", DateTime(timezone=True), nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False),
)

company_table = Table(
    "company_record",
    metadata,
    Column("id", UUID, nullable=False, primary_key=True),
    Column("name", CompanyNameType, nullable=False),
    Column("bio", CompanyDescriptionType, nullable=True),
    Column("verified", Boolean, nullable=False),
    Column("updated_at", DateTime(timezone=True), nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False),
)

session_table = Table(
    "session_record",
    metadata,
    Column("id", UUID, nullable=False, primary_key=True),
    Column("user_id", ForeignKey("user_record.id"), nullable=False),
    Column("host", String, nullable=False),
    Column("token", String, nullable=False),
    Column("token_revision", Integer, nullable=False),
    Column("updated_at", DateTime(timezone=True), nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False),
)

local_authorization_table = Table(
    "local_authorization_record",
    metadata,
    Column("id", UUID, nullable=False, primary_key=True),
    Column("user_id", ForeignKey("user_record.id"), nullable=False),
    Column("password", String(500), nullable=False),
    Column("updated_at", DateTime(timezone=True), nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False),
)


def start_mapper() -> None:
    registry_mapper.map_imperatively(User, user_profile_table)
    registry_mapper.map_imperatively(Company, company_table)
    registry_mapper.map_imperatively(Session, session_table)
    registry_mapper.map_imperatively(LocalAuthorization, local_authorization_table)
