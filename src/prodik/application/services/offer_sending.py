from dataclasses import dataclass
from datetime import datetime
from uuid import uuid4

from prodik.domain.company import Company
from prodik.domain.context import Context, ContextId
from prodik.domain.group import Group, GroupId
from prodik.domain.offer import (
    Offer,
    OfferContext,
    OfferContextId,
    OfferGroup,
    OfferGroupId,
    OfferId,
    OfferLink,
    OfferLinkId,
)
from prodik.domain.role import PermissionType


@dataclass(slots=True, frozen=True, kw_only=True)
class OfferSendingServiceResponse:
    offer: Offer
    offer_groups: list[OfferGroup]
    offer_contexts: list[OfferContext]
    offer_link: OfferLink | None
    from_offer: Offer | None


@dataclass
class OfferSendingService:
    def create_offer_bundle(
        self,
        *,
        title: str,
        description: str,
        from_company: Company,
        to_company: Company,
        requires_counteroffer: bool,
        from_offer: Offer | None,
        groups: list[Group],
        contexts: list[Context],
        group_permissions: dict[GroupId, PermissionType],
        context_permissions: dict[ContextId, PermissionType],
        expires_in: datetime,
    ) -> OfferSendingServiceResponse:
        offer = Offer.new(
            offer_id=OfferId(uuid4()),
            title=title,
            description=description,
            from_company=from_company,
            to_company=to_company,
            requires_counteroffer=requires_counteroffer,
            from_offer=from_offer,
            expires_in=expires_in,
        )

        offer_groups = [
            OfferGroup.new(
                offer_group_id=OfferGroupId(uuid4()),
                offer=offer,
                group=group,
                permission_type=group_permissions[group.id],
            )
            for group in groups
        ]
        offer_contexts = [
            OfferContext.new(
                offer_context_id=OfferContextId(uuid4()),
                offer=offer,
                context=context,
                permission_type=context_permissions[context.id],
            )
            for context in contexts
        ]

        offer_link = None
        if from_offer is not None:
            from_offer.accept()
            offer_link = OfferLink.new(
                offer_link_id=OfferLinkId(uuid4()),
                request_offer=from_offer,
                response_offer=offer,
            )

        return OfferSendingServiceResponse(
            offer=offer,
            offer_groups=offer_groups,
            offer_contexts=offer_contexts,
            offer_link=offer_link,
            from_offer=from_offer,
        )
