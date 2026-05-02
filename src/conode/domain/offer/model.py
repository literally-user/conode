from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from typing import Final, NewType
from uuid import UUID

from conode.domain.company import Company, CompanyId
from conode.domain.context import Context, ContextId
from conode.domain.group import Group, GroupId
from conode.domain.offer.errors import (
    InvalidOfferDescriptionFormatError,
    InvalidOfferTitleFormatError,
)
from conode.domain.shared import Entity, ValueObject

OfferId = NewType("OfferId", UUID)
OfferGroupsId = NewType("OfferGroupsId", UUID)
OfferContextsId = NewType("OfferContextsId", UUID)

MIN_ALLOWED_OFFER_TITLE_LENGTH: Final = 1
MAX_ALLOWED_OFFER_TITLE_LENGTH: Final = 50

MAX_ALLOWED_OFFER_DESCRIPTION_LENGTH: Final = 1000


class OfferStatus(StrEnum):
    PENDING = "PENDING"
    DECLINED = "DECLINED"
    ACCEPTED = "ACCEPTED"


class OfferTitle(ValueObject[str]):
    def __init__(self, value: str) -> None:
        value = value.strip()

        if (
            MIN_ALLOWED_OFFER_TITLE_LENGTH
            <= len(value)
            <= MAX_ALLOWED_OFFER_TITLE_LENGTH
        ):
            raise InvalidOfferTitleFormatError(
                "Offer name must be between"
                f"{MIN_ALLOWED_OFFER_TITLE_LENGTH} and "
                f"{MAX_ALLOWED_OFFER_TITLE_LENGTH}",
                {"key": "name", "value": value},
            )

        super().__init__(value)


class OfferDescription(ValueObject[str]):
    def __init__(self, value: str) -> None:
        value = value.strip()

        if len(value) >= MAX_ALLOWED_OFFER_DESCRIPTION_LENGTH:
            raise InvalidOfferDescriptionFormatError(
                "Offer description must be shorter than "
                f"{MAX_ALLOWED_OFFER_DESCRIPTION_LENGTH}",
                {"key": "name", "value": value},
            )

        super().__init__(value)


@dataclass
class Offer(Entity[OfferId]):
    title: OfferTitle
    description: OfferDescription

    status: OfferStatus

    from_company_id: CompanyId
    to_company_id: CompanyId

    from_offer: OfferId | None

    @classmethod
    def new(
        cls,
        id: OfferId,
        title: str,
        description: str,
        from_company: Company,
        to_company: Company,
        from_offer: "Offer | None",
    ) -> "Offer":
        now = datetime.now(UTC)
        return Offer(
            id=id,
            title=OfferTitle(title),
            description=OfferDescription(description),
            status=OfferStatus.PENDING,
            from_company_id=from_company.id,
            to_company_id=to_company.id,
            from_offer=from_offer.id if from_offer is not None else None,
            created_at=now,
            updated_at=now,
        )


@dataclass
class OfferGroups(Entity[OfferGroupsId]):
    offer_id: OfferId
    group_id: GroupId

    @classmethod
    def new(cls, id: OfferGroupsId, offer: Offer, group: Group) -> "OfferGroups":
        now = datetime.now(UTC)
        return OfferGroups(
            id=id,
            offer_id=offer.id,
            group_id=group.id,
            created_at=now,
            updated_at=now,
        )


@dataclass
class OfferContexts(Entity[OfferContextsId]):
    offer_id: OfferId
    context_id: ContextId

    @classmethod
    def new(
        cls, id: OfferContextsId, offer: Offer, context: Context
    ) -> "OfferContexts":
        now = datetime.now(UTC)
        return OfferContexts(
            id=id,
            offer_id=offer.id,
            context_id=context.id,
            created_at=now,
            updated_at=now,
        )
