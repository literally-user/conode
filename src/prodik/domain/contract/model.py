from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from typing import NewType, Self
from uuid import UUID

from prodik.domain.company import Company, CompanyId
from prodik.domain.contract.errors import InvalidCompanyOffersFormatError
from prodik.domain.offer import Offer, OfferId
from prodik.domain.role import RoleId
from prodik.domain.shared import Entity

ContractId = NewType("ContractId", UUID)


class ContractStatus(StrEnum):
    ACTIVE = "ACTIVE"
    CANCELLED = "CANCELLED"
    EXPIRED = "EXPIRED"


@dataclass
class Contract(Entity[ContractId]):
    company_a_id: CompanyId
    company_b_id: CompanyId

    company_a_offer_id: OfferId | None
    company_b_offer_id: OfferId | None

    company_a_role_id: RoleId | None
    company_b_role_id: RoleId | None

    status: ContractStatus
    expires_in: datetime

    @classmethod
    def new(
        cls,
        contract_id: ContractId,
        company_a: Company,
        company_b: Company,
        company_a_offer: Offer | None,
        company_b_offer: Offer | None,
        company_a_role_id: RoleId | None,
        company_b_role_id: RoleId | None,
        expires_in: datetime,
    ) -> Self:
        if company_a_offer is None and company_b_offer is None:
            raise InvalidCompanyOffersFormatError(
                "Required at least one company offer",
                None,
            )
        if company_a_role_id is None and company_b_role_id is None:
            raise InvalidCompanyOffersFormatError(
                "Required at least one company offer",
                None,
            )
        now = datetime.now(UTC)
        return cls(
            id=contract_id,
            company_a_id=company_a.id,
            company_b_id=company_b.id,
            company_a_offer_id=company_a_offer.id
            if company_a_offer is not None
            else None,
            company_b_offer_id=company_b_offer.id
            if company_b_offer is not None
            else None,
            company_a_role_id=company_a_role_id
            if company_a_role_id is not None
            else None,
            company_b_role_id=company_b_role_id
            if company_b_role_id is not None
            else None,
            status=ContractStatus.ACTIVE,
            expires_in=expires_in,
            created_at=now,
            updated_at=now,
        )
