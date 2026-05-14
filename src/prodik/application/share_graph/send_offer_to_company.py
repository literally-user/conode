from dataclasses import dataclass
from datetime import datetime
from uuid import uuid4

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
from prodik.application.services import AccessControlService
from prodik.domain.company import CompanyId
from prodik.domain.context import ContextId
from prodik.domain.group import GroupId
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

            from_company = await self.company_repository.get_by_id(
                request.from_company_id
            )
            if from_company is None:
                raise CompanyNotFoundError("Company not found", None)

            to_company = await self.company_repository.get_by_id(request.to_company_id)
            if to_company is None:
                raise CompanyNotFoundError("Company not found", None)

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
                    raise OfferNotFoundError("Offer not found", None)

            existing_groups = await self.group_repository.get_all_by_ids(
                list(request.groups.keys())
            )
            existing_contexts = await self.context_repository.get_all_by_ids(
                list(request.contexts.keys())
            )

            if len(existing_groups) != len(request.groups):
                raise GroupNotFoundError("Some of groups not found", None)
            if len(existing_contexts) != len(request.contexts):
                raise ContextNotFoundError("Some of contexts not found", None)

            offer = Offer.new(
                id=OfferId(uuid4()),
                title=request.title,
                description=request.description,
                from_company=from_company,
                to_company=to_company,
                requires_counteroffer=request.requires_counteroffer,
                from_offer=from_offer,
                expires_in=request.expires_in,
            )

            offer_groups = [
                OfferGroup.new(
                    id=OfferGroupId(uuid4()),
                    offer=offer,
                    group=group,
                    permission_type=request.groups[group.id],
                )
                for group in existing_groups
            ]

            offer_contexts = [
                OfferContext.new(
                    id=OfferContextId(uuid4()),
                    offer=offer,
                    context=context,
                    permission_type=request.contexts[context.id],
                )
                for context in existing_contexts
            ]

            await self.offer_repository.create(offer)

            if from_offer is not None:
                from_offer.accept()
                offer_link = OfferLink.new(
                    id=OfferLinkId(uuid4()),
                    request_offer=from_offer,
                    response_offer=offer,
                )

                await self.offer_link_repository.create(offer_link)
                await self.offer_repository.update(from_offer)

            await self.offer_group_repository.create_all(offer_groups)
            await self.offer_context_repository.create_all(offer_contexts)

            return offer
