from dataclasses import dataclass
from uuid import uuid4

from prodik.application.interfaces.repositories import OfferLinkRepository
from prodik.domain.offer import Offer, OfferLink, OfferLinkId


@dataclass(slots=True)
class OfferLinkFactory:
    offer_link_repository: OfferLinkRepository

    async def create_link(
        self,
        *,
        request_offer: Offer,
        response_offer: Offer,
    ) -> OfferLink:
        offer_link = OfferLink.new(
            id=OfferLinkId(uuid4()),
            request_offer=request_offer,
            response_offer=response_offer,
        )

        await self.offer_link_repository.create(offer_link)

        return offer_link
