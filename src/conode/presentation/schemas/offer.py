from datetime import datetime

from pydantic import BaseModel

from conode.domain.company import CompanyId
from conode.domain.context import ContextId
from conode.domain.group import GroupId
from conode.domain.offer import OfferId, OfferStatus
from conode.domain.role import PermissionType


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
