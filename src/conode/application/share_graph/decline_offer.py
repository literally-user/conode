from dataclasses import dataclass

from conode.application.errors import (
    OfferLinkNotFoundError,
)
from conode.application.interfaces.repositories import (
    CompanyRepository,
    OfferLinkRepository,
    OfferRepository,
)
from conode.application.interfaces.transaction_manager import TransactionManager
from conode.application.services import AccessControlService
from conode.domain.offer import OfferId


@dataclass
class DeclineOfferInteractor:
    transaction_manager: TransactionManager
    offer_link_repository: OfferLinkRepository
    offer_repository: OfferRepository
    access_control_service: AccessControlService
    company_repository: CompanyRepository

    async def execute(self, offer_id: OfferId) -> None:
        user = await self.access_control_service.get_authorized_user()

        async with self.transaction_manager:
            offer = await self.offer_repository.get_by_id(offer_id)
            company = await self.company_repository.get_by_id(offer.to_company_id)

            await self.access_control_service.ensure_user_can_manipulate_offers(
                user,
                company,
            )

            if offer.is_counter_offer():
                from_offer = await self.offer_repository.get_by_id(
                    offer.get_from_offer_id(),
                )

                offer_link = await self.offer_link_repository.get_by_offers_ids(
                    offer.id,
                    from_offer.id,
                )
                if offer_link is None:
                    raise OfferLinkNotFoundError(
                        "Offer link not found",
                        [
                            {"key": "to_offer_id", "value": offer.id},
                            {"key": "from_offer_id", "value": from_offer.id},
                        ],
                    )

                from_offer.decline()
                offer_link.abort()

                await self.offer_repository.update(from_offer)
                await self.offer_link_repository.update(offer_link)

            offer.decline()

            await self.offer_repository.update(offer)
