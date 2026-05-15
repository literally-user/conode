from datetime import datetime

from pydantic import BaseModel

from prodik.domain.company import CompanyId
from prodik.domain.context import ContextId
from prodik.domain.group import GroupId
from prodik.domain.offer import OfferId, OfferStatus
from prodik.domain.role import PermissionType


class SendOfferToCompanyRequest(BaseModel):
    title: str
    description: str
    from_company_id: CompanyId
    to_company_id: CompanyId
    requires_counteroffer: bool
    from_offer_id: OfferId | None
    groups: dict[GroupId, PermissionType]
    contexts: dict[ContextId, PermissionType]
    expires_in: datetime


class OfferSchema(BaseModel):
    id: OfferId
    title: str
    description: str

    status: OfferStatus

    from_company_id: CompanyId
    to_company_id: CompanyId

    from_offer: OfferId | None
    requires_counteroffer: bool
    expires_in: datetime
