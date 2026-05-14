from dataclasses import dataclass
from itertools import chain
from uuid import uuid4

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
from prodik.application.services import AccessControlService
from prodik.domain.contract import Contract, ContractId
from prodik.domain.offer import OfferId
from prodik.domain.role import (
    EntityType,
    Role,
    RoleId,
    RolePermission,
    RolePermissionId,
)


@dataclass
class AcceptOfferInteractor:
    access_control_service: AccessControlService
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
                raise OfferNotFoundError("Offer not found", None)

            offer_from_company = await self.company_repository.get_by_id(
                offer.from_company_id
            )
            if offer_from_company is None:
                raise CompanyNotFoundError("Company not found", None)

            offer_to_company = await self.company_repository.get_by_id(
                offer.to_company_id
            )
            if offer_to_company is None:
                raise CompanyNotFoundError("Company not found", None)

            await self.access_control_service.ensure_user_can_manipulate_offers(
                user,
                offer_to_company,
            )

            offer.accept()

            from_offer = None
            from_company_role = None
            if offer.is_counter_offer():
                from_offer = await self.offer_repository.get_by_id(
                    offer.get_from_offer_id()
                )
                if from_offer is None:
                    raise OfferNotFoundError("Offer not found", None)

                offer_link = await self.offer_link_repository.get_by_offers_ids(
                    offer.id, from_offer.id
                )
                if offer_link is None:
                    raise OfferLinkNotFoundError("Offer link not found", None)

                from_company_offer_groups = (
                    await self.offer_group_repository.get_by_offer_id(offer.id)
                )
                from_company_offer_contexts = (
                    await self.offer_context_repository.get_by_offer_id(offer.id)
                )

                from_company_role = Role.new(
                    id=RoleId(uuid4()),
                    name=f"{offer_from_company.name}-{offer_to_company.name}",
                    company=offer_to_company,
                )

                from_company_role_group_permissions = [
                    RolePermission.new(
                        id=RolePermissionId(uuid4()),
                        role=from_company_role,
                        permission=offer_group.permission_type,
                        entity_type=EntityType.GROUP,
                        entity_id=offer_group.group_id,
                    )
                    for offer_group in from_company_offer_groups
                ]
                from_company_role_context_permissions = [
                    RolePermission.new(
                        id=RolePermissionId(uuid4()),
                        role=from_company_role,
                        permission=offer_context.permission_type,
                        entity_type=EntityType.CONTEXT,
                        entity_id=offer_context.context_id,
                    )
                    for offer_context in from_company_offer_contexts
                ]

                from_offer.accept()
                offer_link.accept()

                await self.role_repository.create(from_company_role)
                await self.role_permissions_repository.create_all(
                    list(
                        chain(
                            from_company_role_context_permissions,
                            from_company_role_group_permissions,
                        )
                    )
                )
                await self.offer_link_repository.update(offer_link)
                await self.offer_repository.update(from_offer)

            company_role = Role.new(
                id=RoleId(uuid4()),
                name=f"{offer_to_company.name}-{offer_from_company.name}",
                company=offer_to_company,
            )

            company_offer_groups = await self.offer_group_repository.get_by_offer_id(
                offer.id
            )
            company_offer_contexts = await self.offer_group_repository.get_by_offer_id(
                offer.id
            )
            from_company_role_group_permissions = [
                RolePermission.new(
                    id=RolePermissionId(uuid4()),
                    role=company_role,
                    permission=offer_group.permission_type,
                    entity_type=EntityType.GROUP,
                    entity_id=offer_group.group_id,
                )
                for offer_group in company_offer_groups
            ]
            from_company_role_context_permissions = [
                RolePermission.new(
                    id=RolePermissionId(uuid4()),
                    role=company_role,
                    permission=offer_context.permission_type,
                    entity_type=EntityType.CONTEXT,
                    entity_id=offer_context.group_id,
                )
                for offer_context in company_offer_contexts
            ]

            contract = Contract.new(
                id=ContractId(uuid4()),
                company_a=offer_to_company,
                company_b=offer_from_company,
                company_a_offer=offer,
                company_b_offer=from_offer,
                expires_in=offer.expires_in,
                company_a_role_id=company_role.id,
                company_b_role_id=from_company_role.id
                if from_company_role is not None
                else None,
            )

            await self.role_repository.create(company_role)
            await self.role_permissions_repository.create_all(
                list(
                    chain(
                        from_company_role_context_permissions,
                        from_company_role_group_permissions,
                    )
                )
            )
            await self.contract_repository.create(contract)

            return contract
