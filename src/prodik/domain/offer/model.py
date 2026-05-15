from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from typing import Final, NewType
from uuid import UUID

from prodik.domain.company import Company, CompanyId
from prodik.domain.context import Context, ContextId
from prodik.domain.group import Group, GroupId
from prodik.domain.offer.errors import (
    InvalidOfferDescriptionFormatError,
    InvalidOfferTitleFormatError,
    OfferCannotAnswerToItselfError,
    OfferCannotCreateChainsError,
    OfferCannotExpireAtPastError,
    OfferIsNotCounterOfferError,
)
from prodik.domain.role import PermissionType
from prodik.domain.shared import Entity, ValueObject

OfferId = NewType("OfferId", UUID)
OfferLinkId = NewType("OfferLinkId", UUID)
OfferGroupId = NewType("OfferGroupId", UUID)
OfferContextId = NewType("OfferContextId", UUID)

MIN_ALLOWED_OFFER_TITLE_LENGTH: Final = 1
MAX_ALLOWED_OFFER_TITLE_LENGTH: Final = 50

MAX_ALLOWED_OFFER_DESCRIPTION_LENGTH: Final = 1000


class OfferLinkStatus(StrEnum):
    ACCEPTED = "ACCEPTED"
    ABORTED = "ABORTED"
    PENDING = "PENDING"


class OfferStatus(StrEnum):
    PENDING = "PENDING"
    DECLINED = "DECLINED"
    ACCEPTED = "ACCEPTED"


class OfferTitle(ValueObject[str]):
    def __init__(self, value: str) -> None:
        value = value.strip()

        if (
            MAX_ALLOWED_OFFER_TITLE_LENGTH
            <= len(value)
            <= MIN_ALLOWED_OFFER_TITLE_LENGTH
        ):
            raise InvalidOfferTitleFormatError(
                "Offer name must be between "
                f"{MIN_ALLOWED_OFFER_TITLE_LENGTH} and "
                f"{MAX_ALLOWED_OFFER_TITLE_LENGTH}",
                [{"key": "name", "value": value}],
            )

        super().__init__(value)


class OfferDescription(ValueObject[str]):
    def __init__(self, value: str) -> None:
        value = value.strip()

        if len(value) >= MAX_ALLOWED_OFFER_DESCRIPTION_LENGTH:
            raise InvalidOfferDescriptionFormatError(
                "Offer description must be shorter than "
                f"{MAX_ALLOWED_OFFER_DESCRIPTION_LENGTH}",
                [{"key": "name", "value": value}],
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
    requires_counteroffer: bool
    expires_in: datetime

    @classmethod
    def new(
        cls,
        id: OfferId,
        title: str,
        description: str,
        from_company: Company,
        to_company: Company,
        from_offer: "Offer | None",
        expires_in: datetime,
        *,
        requires_counteroffer: bool,
    ) -> "Offer":
        if from_offer is not None and from_offer.id == id:
            raise OfferCannotAnswerToItselfError(
                "Offer cannot answer to itself",
                [
                    {"key": "from_offer", "value": from_offer},
                ],
            )

        if from_offer is not None and from_offer.is_counter_offer():
            raise OfferCannotCreateChainsError(
                "Offer cannot create chains",
                [
                    {"key": "from_offer", "value": from_offer},
                    {"key": "requires_counteroffer", "value": requires_counteroffer},
                ],
            )

        now = datetime.now(UTC)
        if expires_in.timestamp() < now.timestamp():
            raise OfferCannotExpireAtPastError("Offer cannot expire at past", None)
        return Offer(
            id=id,
            title=OfferTitle(title),
            description=OfferDescription(description),
            status=OfferStatus.PENDING,
            from_company_id=from_company.id,
            to_company_id=to_company.id,
            from_offer=from_offer.id if from_offer is not None else None,
            requires_counteroffer=requires_counteroffer,
            expires_in=expires_in,
            created_at=now,
            updated_at=now,
        )

    def accept(self) -> None:
        self.status = OfferStatus.ACCEPTED
        self.touch()

    def decline(self) -> None:
        self.status = OfferStatus.DECLINED
        self.touch()

    def is_counter_offer(self) -> bool:
        return self.from_offer is not None

    def get_from_offer_id(self) -> OfferId:
        if self.from_offer is None:
            raise OfferIsNotCounterOfferError("Not a counter offer", None)

        return self.from_offer


@dataclass
class OfferGroup(Entity[OfferGroupId]):
    offer_id: OfferId
    group_id: GroupId
    permission_type: PermissionType

    @classmethod
    def new(
        cls,
        id: OfferGroupId,
        offer: Offer,
        group: Group,
        permission_type: PermissionType,
    ) -> "OfferGroup":
        now = datetime.now(UTC)
        return OfferGroup(
            id=id,
            offer_id=offer.id,
            group_id=group.id,
            permission_type=permission_type,
            created_at=now,
            updated_at=now,
        )


@dataclass
class OfferContext(Entity[OfferContextId]):
    offer_id: OfferId
    context_id: ContextId
    permission_type: PermissionType

    @classmethod
    def new(
        cls,
        id: OfferContextId,
        offer: Offer,
        context: Context,
        permission_type: PermissionType,
    ) -> "OfferContext":
        now = datetime.now(UTC)
        return OfferContext(
            id=id,
            offer_id=offer.id,
            context_id=context.id,
            permission_type=permission_type,
            created_at=now,
            updated_at=now,
        )


@dataclass
class OfferLink(Entity[OfferLinkId]):
    request_offer_id: OfferId
    response_offer_id: OfferId
    status: OfferLinkStatus

    @classmethod
    def new(
        cls, id: OfferLinkId, request_offer: Offer, response_offer: Offer
    ) -> "OfferLink":
        now = datetime.now(UTC)
        return OfferLink(
            id=id,
            request_offer_id=request_offer.id,
            response_offer_id=response_offer.id,
            status=OfferLinkStatus.PENDING,
            created_at=now,
            updated_at=now,
        )

    def accept(self) -> None:
        self.status = OfferLinkStatus.ACCEPTED
        self.touch()

    def abort(self) -> None:
        self.status = OfferLinkStatus.ABORTED
        self.touch()
