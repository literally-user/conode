import asyncio
from dataclasses import dataclass
from datetime import datetime

from prodik.application.errors import (
    CompanyNotFoundError,
    ContextNotFoundError,
    GroupNotFoundError,
    OfferNotFoundError,
)
from prodik.application.interfaces.repositories import (
    CompanyRepository,
    ContextRepository,
    GroupRepository,
    OfferContextRepository,
    OfferGroupRepository,
    OfferLinkRepository,
    OfferRepository,
)
from prodik.application.interfaces.transaction_manager import TransactionManager
from prodik.application.services import AccessControlService, OfferSendingService
from prodik.domain.company import CompanyId
from prodik.domain.context import ContextId
from prodik.domain.group import GroupId
from prodik.domain.offer import Offer, OfferId
from prodik.domain.role import PermissionType


@dataclass(frozen=True, slots=True, kw_only=True)
class SendOfferToCompanyRequestDTO:
    title: str
    description: str
    from_company_id: CompanyId
    to_company_id: CompanyId
    requires_counteroffer: bool
    from_offer_id: OfferId | None
    groups: dict[GroupId, PermissionType]
    contexts: dict[ContextId, PermissionType]
    expires_in: datetime


@dataclass
class SendOfferToCompanyInteractor:
    offer_sending_service: OfferSendingService
    offer_repository: OfferRepository
    offer_group_repository: OfferGroupRepository
    offer_context_repository: OfferContextRepository
    company_repository: CompanyRepository
    offer_link_repository: OfferLinkRepository
    transaction_manager: TransactionManager
    access_control_service: AccessControlService
    group_repository: GroupRepository
    context_repository: ContextRepository

    async def execute(self, request: SendOfferToCompanyRequestDTO) -> Offer:
        async with self.transaction_manager:
            user = await self.access_control_service.get_authorized_user()

            from_company, to_company = await asyncio.gather(
                self.company_repository.get_by_id(request.from_company_id),
                self.company_repository.get_by_id(request.to_company_id),
            )
            if from_company is None:
                raise CompanyNotFoundError(
                    "Company not found",
                    [{"key": "company_id", "value": request.from_company_id}],
                )
            if to_company is None:
                raise CompanyNotFoundError(
                    "Company not found",
                    [{"key": "company_id", "value": request.to_company_id}],
                )

            await self.access_control_service.ensure_user_can_send_offers(
                user,
                from_company,
            )

            from_offer = None
            if request.from_offer_id is not None:
                from_offer = await self.offer_repository.get_by_id(
                    request.from_offer_id
                )
                if from_offer is None:
                    raise OfferNotFoundError(
                        "Offer not found",
                        [{"key": "offer_id", "value": request.from_offer_id}],
                    )

            existing_groups = await self.group_repository.get_all_by_ids(
                list(request.groups.keys())
            )
            existing_contexts = await self.context_repository.get_all_by_ids(
                list(request.contexts.keys())
            )

            if len(existing_groups) != len(request.groups):
                raise GroupNotFoundError(
                    "Some of groups not found",
                    [
                        {
                            "key": "group_ids",
                            "value": list(request.groups.keys()),
                        }
                    ],
                )
            if len(existing_contexts) != len(request.contexts):
                raise ContextNotFoundError(
                    "Some of contexts not found",
                    [
                        {
                            "key": "context_ids",
                            "value": list(request.contexts.keys()),
                        }
                    ],
                )

            offer_bundle = self.offer_sending_service.create_offer_bundle(
                title=request.title,
                description=request.description,
                from_company=from_company,
                to_company=to_company,
                requires_counteroffer=request.requires_counteroffer,
                from_offer=from_offer,
                groups=existing_groups,
                contexts=existing_contexts,
                group_permissions=request.groups,
                context_permissions=request.contexts,
                expires_in=request.expires_in,
            )

            await self.offer_repository.create(offer_bundle.offer)
            await self.offer_group_repository.create_all(offer_bundle.offer_groups)
            await self.offer_context_repository.create_all(offer_bundle.offer_contexts)

            if offer_bundle.offer_link is not None:
                await self.offer_link_repository.create(offer_bundle.offer_link)
            if offer_bundle.from_offer is not None:
                await self.offer_repository.update(offer_bundle.from_offer)

            return offer_bundle.offer
