from dataclasses import dataclass
from datetime import UTC, datetime
from typing import NewType, Self
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
    def new(
        cls, company_grant_id: CompanyGrantId, role: Role, company: Company
    ) -> Self:
        now = datetime.now(UTC)
        return cls(
            id=company_grant_id,
            company_id=company.id,
            role_id=role.id,
            created_at=now,
            updated_at=now,
        )
