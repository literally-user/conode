from dataclasses import dataclass
from uuid import uuid4

from prodik.domain.company import Company
from prodik.domain.contract import Contract, ContractId
from prodik.domain.offer import Offer, OfferLink
from prodik.domain.role import RoleId


@dataclass(slots=True, frozen=True, kw_only=True)
class OfferAcceptanceServiceResponse:
    offer: Offer
    from_offer: Offer | None
    offer_link: OfferLink | None


@dataclass
class OfferAcceptanceService:
    def accept(
        self,
        offer: Offer,
        from_offer: Offer | None,
        offer_link: OfferLink | None,
    ) -> OfferAcceptanceServiceResponse:
        offer.accept()

        if offer.is_counter_offer():
            if from_offer is None or offer_link is None:
                raise ValueError("Counter offer requires source offer and offer link")

            from_offer.accept()
            offer_link.accept()

        return OfferAcceptanceServiceResponse(
            offer=offer,
            from_offer=from_offer,
            offer_link=offer_link,
        )

    def create_contract(
        self,
        *,
        company_a: Company,
        company_b: Company,
        company_a_offer: Offer | None,
        company_b_offer: Offer | None,
        company_a_role_id: RoleId | None,
        company_b_role_id: RoleId | None,
    ) -> Contract:
        return Contract.new(
            id=ContractId(uuid4()),
            company_a=company_a,
            company_b=company_b,
            company_a_offer=company_a_offer,
            company_b_offer=company_b_offer,
            expires_in=company_a_offer.expires_in
            if company_a_offer is not None
            else company_b_offer.expires_in,  # type: ignore
            company_a_role_id=company_a_role_id,
            company_b_role_id=company_b_role_id,
        )
