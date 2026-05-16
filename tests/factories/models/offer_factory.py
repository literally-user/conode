import asyncio
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from uuid import uuid4

from prodik.application.interfaces.repositories import (
    OfferContextRepository,
    OfferGroupRepository,
    OfferRepository,
)
from prodik.domain.company import Company
from prodik.domain.context import ContextId
from prodik.domain.group import GroupId
from prodik.domain.offer import (
    Offer,
    OfferContext,
    OfferContextId,
    OfferGroup,
    OfferGroupId,
    OfferId,
)
from prodik.domain.role import PermissionType
from tests.factories.common import generate_random_string
from tests.factories.models.company_factory import CompanyFactory
from tests.factories.models.context_factory import ContextFactory
from tests.factories.models.group_factory import GroupFactory
from tests.factories.models.offer_link_factory import OfferLinkFactory


@dataclass(slots=True)
class OfferFactory:
    offer_repository: OfferRepository
    offer_group_repository: OfferGroupRepository
    offer_context_repository: OfferContextRepository

    offer_link_factory: OfferLinkFactory

    company_factory: CompanyFactory
    group_factory: GroupFactory
    context_factory: ContextFactory

    async def create_offer(
        self,
        *,
        from_company: Company | None = None,
        to_company: Company | None = None,
        from_offer: Offer | None = None,
        requires_counteroffer: bool = False,
        groups: dict[GroupId, PermissionType | str] | None = None,
        contexts: dict[ContextId, PermissionType | str] | None = None,
    ) -> Offer:
        if from_company is None:
            from_company = await self.company_factory.create_company()

        if to_company is None:
            to_company = await self.company_factory.create_company()

        offer = Offer.new(
            offer_id=OfferId(uuid4()),
            title=generate_random_string(15),
            description=generate_random_string(100),
            from_company=from_company,
            to_company=to_company,
            from_offer=from_offer,
            expires_in=datetime.now(UTC) + timedelta(days=7),
            requires_counteroffer=requires_counteroffer,
        )

        await self.offer_repository.create(offer)

        offer_groups: list[OfferGroup] = []
        offer_contexts: list[OfferContext] = []

        if groups is None:
            default_group = await self.group_factory.create_group(company=from_company)
            groups = {
                default_group.id: PermissionType.READ,
            }

        if contexts is None:
            default_context = await self.context_factory.create_context(
                company=from_company
            )
            contexts = {
                default_context.id: PermissionType.READ,
            }

        for group_id, permission in groups.items():
            permission_type = (
                PermissionType(permission)
                if isinstance(permission, str)
                else permission
            )

            offer_groups.append(
                OfferGroup(
                    id=OfferGroupId(uuid4()),
                    offer_id=offer.id,
                    group_id=group_id,
                    permission_type=permission_type,
                    created_at=datetime.now(UTC),
                    updated_at=datetime.now(UTC),
                )
            )

        for context_id, permission in contexts.items():
            permission_type = (
                PermissionType(permission)
                if isinstance(permission, str)
                else permission
            )

            offer_contexts.append(
                OfferContext(
                    id=OfferContextId(uuid4()),
                    offer_id=offer.id,
                    context_id=context_id,
                    permission_type=permission_type,
                    created_at=datetime.now(UTC),
                    updated_at=datetime.now(UTC),
                )
            )

        await asyncio.gather(
            self.offer_group_repository.create_all(offer_groups),
            self.offer_context_repository.create_all(offer_contexts),
        )

        return offer

    async def create_counter_offer(
        self,
        *,
        from_company: Company,
        to_company: Company,
        from_offer: Offer,
        groups: dict[GroupId, PermissionType | str] | None = None,
        contexts: dict[ContextId, PermissionType | str] | None = None,
    ) -> Offer:
        counter_offer = await self.create_offer(
            from_company=from_company,
            to_company=to_company,
            from_offer=from_offer,
            requires_counteroffer=True,
            groups=groups,
            contexts=contexts,
        )

        await self.offer_link_factory.create_link(
            request_offer=from_offer,
            response_offer=counter_offer,
        )

        return counter_offer

    async def create_counter_offer_without_link(
        self,
        *,
        from_company: Company,
        to_company: Company,
        from_offer: Offer,
        groups: dict[GroupId, PermissionType | str] | None = None,
        contexts: dict[ContextId, PermissionType | str] | None = None,
    ) -> Offer:
        return await self.create_offer(
            from_company=from_company,
            to_company=to_company,
            from_offer=from_offer,
            requires_counteroffer=True,
            groups=groups,
            contexts=contexts,
        )
