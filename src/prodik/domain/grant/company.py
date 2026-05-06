from dataclasses import dataclass
from datetime import UTC, datetime
from typing import NewType
from uuid import UUID

from prodik.domain.company import Company, CompanyId
from prodik.domain.role import Role, RoleId
from prodik.domain.shared import Entity

CompanyGrantId = NewType("CompanyGrantId", UUID)


@dataclass
class CompanyGrant(Entity[CompanyGrantId]):
    company_id: CompanyId
    role_id: RoleId

    @classmethod
    def new(cls, id: CompanyGrantId, role: Role, company: Company) -> "CompanyGrant":
        now = datetime.now(UTC)
        return CompanyGrant(
            id=id,
            company_id=company.id,
            role_id=role.id,
            created_at=now,
            updated_at=now,
        )
