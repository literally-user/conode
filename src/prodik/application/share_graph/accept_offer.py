import asyncio
from dataclasses import dataclass
from typing import cast

from prodik.application.errors import (
    CompanyNotFoundError,
    OfferLinkNotFoundError,
    OfferNotFoundError,
)
from prodik.application.interfaces.repositories import (
    CompanyRepository,
    ContractRepository,
    OfferContextRepository,
    OfferGroupRepository,
    OfferLinkRepository,
    OfferRepository,
    RolePermissionsRepository,
    RoleRepository,
)
from prodik.application.interfaces.transaction_manager import TransactionManager
from prodik.application.services import (
    AccessControlService,
    OfferAcceptanceService,
    RoleManagmentService,
)
from prodik.domain.company import Company
from prodik.domain.contract import Contract
from prodik.domain.offer import Offer, OfferContext, OfferGroup, OfferId
from prodik.domain.role import EntityType, PermissionType, RolePermissionEntityId


@dataclass
class AcceptOfferInteractor:
    access_control_service: AccessControlService
    role_managment_service: RoleManagmentService
    offer_acceptance_service: OfferAcceptanceService
    transaction_manager: TransactionManager
    offer_repository: OfferRepository
    offer_link_repository: OfferLinkRepository
    role_repository: RoleRepository
    role_permissions_repository: RolePermissionsRepository
    contract_repository: ContractRepository
    company_repository: CompanyRepository
    offer_group_repository: OfferGroupRepository
    offer_context_repository: OfferContextRepository

    async def execute(self, offer_id: OfferId) -> Contract:
        async with self.transaction_manager:
            user = await self.access_control_service.get_authorized_user()
            offer = await self.offer_repository.get_by_id(offer_id)
            if offer is None:
                raise OfferNotFoundError(
                    "Offer not found",
                    [{"key": "offer_id", "value": offer_id}],
                )

            offer_from_company, offer_to_company = await self._get_offer_companies(
                offer,
            )
            await self.access_control_service.ensure_user_can_manipulate_offers(
                user,
                offer_to_company,
            )

            from_offer = None
            from_company_role_managment_response = None
            offer_link = None

            if offer.is_counter_offer():
                from_offer = await self.offer_repository.get_by_id(
                    offer.get_from_offer_id(),
                )
                if from_offer is None:
                    raise OfferNotFoundError(
                        "Counter offer not found",
                        [{"key": "offer_id", "value": offer.get_from_offer_id()}],
                    )

                offer_link = await self.offer_link_repository.get_by_offers_ids(
                    offer.id,
                    from_offer.id,
                )
                if offer_link is None:
                    raise OfferLinkNotFoundError(
                        "Offer link by offer ids not found",
                        [
                            {"key": "to_offer_id", "value": offer.id},
                            {"key": "from_offer_id", "value": from_offer.id},
                        ],
                    )

                from_company_permissions = await self._get_offer_permissions(offer.id)
                from_company_role_managment_response = (
                    self.role_managment_service.create_role_with_permissions(
                        name=f"{offer_from_company.name}-{offer_to_company.name}",
                        company=offer_to_company,
                        request=from_company_permissions,
                    )
                )

                await self.role_repository.create(
                    from_company_role_managment_response.role,
                )
                await self.role_permissions_repository.create_all(
                    from_company_role_managment_response.permissions,
                )

            acceptance_result = self.offer_acceptance_service.accept(
                offer=offer,
                from_offer=from_offer,
                offer_link=offer_link,
            )

            if acceptance_result.offer_link is not None:
                await self.offer_link_repository.update(acceptance_result.offer_link)
            if acceptance_result.from_offer is not None:
                await self.offer_repository.update(acceptance_result.from_offer)

            to_company_permissions = await self._get_offer_permissions(offer.id)
            to_company_role_managment_response = (
                self.role_managment_service.create_role_with_permissions(
                    name=f"{offer_to_company.name}-{offer_from_company.name}",
                    company=offer_to_company,
                    request=to_company_permissions,
                )
            )

            contract = self.offer_acceptance_service.create_contract(
                company_a=offer_to_company,
                company_b=offer_from_company,
                company_a_offer=offer,
                company_b_offer=from_offer,
                company_a_role_id=to_company_role_managment_response.role.id,
                company_b_role_id=from_company_role_managment_response.role.id
                if from_company_role_managment_response is not None
                else None,
            )

            await self.role_repository.create(to_company_role_managment_response.role)
            await self.role_permissions_repository.create_all(
                to_company_role_managment_response.permissions,
            )
            await self.contract_repository.create(contract)

            return contract

    async def _get_offer_companies(self, offer: Offer) -> tuple[Company, Company]:
        from_company, to_company = await asyncio.gather(
            self.company_repository.get_by_id(offer.from_company_id),
            self.company_repository.get_by_id(offer.to_company_id),
        )

        if from_company is None or to_company is None:
            raise CompanyNotFoundError(
                "Company not found",
                [
                    {"key": "from_company_id", "value": offer.from_company_id},
                    {"key": "to_company_id", "value": offer.to_company_id},
                ],
            )

        return from_company, to_company

    async def _get_offer_permissions(
        self,
        offer_id: OfferId,
    ) -> list[tuple[RolePermissionEntityId, EntityType, PermissionType]]:
        offer_groups, offer_contexts = await asyncio.gather(
            self.offer_group_repository.get_by_offer_id(offer_id),
            self.offer_context_repository.get_by_offer_id(offer_id),
        )
        return self._compile_permissions(offer_groups, offer_contexts)

    def _compile_permissions(
        self,
        offer_groups: list[OfferGroup],
        offer_contexts: list[OfferContext],
    ) -> list[tuple[RolePermissionEntityId, EntityType, PermissionType]]:
        return [
            (
                cast("RolePermissionEntityId", group.group_id),
                EntityType.GROUP,
                group.permission_type,
            )
            for group in offer_groups
        ] + [
            (
                cast("RolePermissionEntityId", context.context_id),
                EntityType.CONTEXT,
                context.permission_type,
            )
            for context in offer_contexts
        ]
