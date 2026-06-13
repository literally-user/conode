from dataclasses import dataclass

import structlog
from sqlalchemy import and_, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from prodik.application.interfaces.repositories import (
    OfferContextRepository,
    OfferGroupRepository,
    OfferLinkRepository,
    OfferRepository,
)
from prodik.domain.offer.model import (
    Offer,
    OfferContext,
    OfferGroup,
    OfferId,
    OfferLink,
)

logger = structlog.get_logger()


@dataclass
class OfferRepositoryImpl(OfferRepository):
    session: AsyncSession

    async def create(self, offer: Offer) -> None:
        logger.info("Repository create offer", offer_id=offer.id)
        await self.session.execute(
            insert(Offer).values(
                id=offer.id,
                title=offer.title,
                description=offer.description,
                status=offer.status,
                from_company_id=offer.from_company_id,
                to_company_id=offer.to_company_id,
                from_offer=offer.from_offer,
                requires_counteroffer=offer.requires_counteroffer,
                expires_in=offer.expires_in,
                created_at=offer.created_at,
                updated_at=offer.updated_at,
            ),
        )

    async def update(self, offer: Offer) -> None:
        logger.info("Repository update offer", offer_id=offer.id)
        await self.session.execute(
            update(Offer)
            .where(
                Offer.id == offer.id,  # type: ignore
            )
            .values(
                title=offer.title,
                description=offer.description,
                status=offer.status,
                from_company_id=offer.from_company_id,
                to_company_id=offer.to_company_id,
                from_offer=offer.from_offer,
                requires_counteroffer=offer.requires_counteroffer,
            ),
        )

    async def get_by_id(self, offer_id: OfferId) -> Offer | None:
        logger.info("Repository get offer by id", offer_id=offer_id)
        result = await self.session.execute(
            select(Offer).where(
                Offer.id == offer_id,  # type: ignore
            ),
        )

        offer = result.scalar_one_or_none()
        logger.info("Repository fetched offer by id", found=offer is not None)
        return offer


@dataclass
class OfferLinkRepositoryImpl(OfferLinkRepository):
    session: AsyncSession

    async def create(self, offer_link: OfferLink) -> None:
        logger.info("Repository create offer link", offer_link_id=offer_link.id)
        await self.session.execute(
            insert(OfferLink).values(
                id=offer_link.id,
                request_offer_id=offer_link.request_offer_id,
                response_offer_id=offer_link.response_offer_id,
                status=offer_link.status,
                created_at=offer_link.created_at,
                updated_at=offer_link.updated_at,
            ),
        )

    async def update(self, offer_link: OfferLink) -> None:
        logger.info("Repository update offer link", offer_link_id=offer_link.id)
        await self.session.execute(
            update(OfferLink)
            .where(
                OfferLink.id == offer_link.id,  # type: ignore
            )
            .values(
                request_offer_id=offer_link.request_offer_id,
                response_offer_id=offer_link.response_offer_id,
                status=offer_link.status,
            ),
        )

    async def get_by_offers_ids(
        self,
        from_offer_id: OfferId,
        to_offer_id: OfferId,
    ) -> OfferLink | None:
        logger.info(
            "Repository get offer link by offer ids",
            from_offer_id=from_offer_id,
            to_offer_id=to_offer_id,
        )
        result = await self.session.execute(
            select(OfferLink).where(
                and_(
                    OfferLink.request_offer_id == to_offer_id,  # type: ignore
                    OfferLink.response_offer_id == from_offer_id,  # type: ignore
                ),
            ),
        )
        logger.info("Repository fetched offer link by id", found=result is not None)

        return result.scalar_one_or_none()


@dataclass
class OfferGroupRepositoryImpl(OfferGroupRepository):
    session: AsyncSession

    async def create_all(self, offer_groups: list[OfferGroup]) -> None:
        logger.info(
            "Repository create offer groups",
            request_count=len(offer_groups),
        )
        if not offer_groups:
            return

        await self.session.execute(
            insert(OfferGroup).values(
                [
                    {
                        "id": group.id,
                        "offer_id": group.offer_id,
                        "group_id": group.group_id,
                        "permission_type": group.permission_type,
                        "created_at": group.created_at,
                        "updated_at": group.updated_at,
                    }
                    for group in offer_groups
                ],
            ),
        )

    async def get_by_offer_id(self, offer_id: OfferId) -> list[OfferGroup]:
        logger.info("Repository get offer group by offer id")
        result = await self.session.execute(
            select(OfferGroup).where(
                OfferGroup.offer_id == offer_id,  # type: ignore
            ),
        )

        result_offer_groups = list(result.scalars().all())
        logger.info(
            "Repository offer groups by offer id",
            found_count=len(result_offer_groups),
        )

        return result_offer_groups


@dataclass
class OfferContextRepositoryImpl(OfferContextRepository):
    session: AsyncSession

    async def create_all(self, offer_contexts: list[OfferContext]) -> None:
        logger.info(
            "Repository create offer contexts",
            request_count=len(offer_contexts),
        )

        if not offer_contexts:
            return

        await self.session.execute(
            insert(OfferContext).values(
                [
                    {
                        "id": context.id,
                        "offer_id": context.offer_id,
                        "context_id": context.context_id,
                        "permission_type": context.permission_type,
                        "created_at": context.created_at,
                        "updated_at": context.updated_at,
                    }
                    for context in offer_contexts
                ],
            ),
        )

    async def get_by_offer_id(self, offer_id: OfferId) -> list[OfferContext]:
        logger.info("Repository get offer group by offer id")
        result = await self.session.execute(
            select(OfferContext).where(
                OfferContext.offer_id == offer_id,  # type: ignore
            ),
        )

        result_offer_contexts = list(result.scalars().all())
        logger.info(
            "Repository offer contexts by offer id",
            found_count=len(result_offer_contexts),
        )

        return result_offer_contexts
