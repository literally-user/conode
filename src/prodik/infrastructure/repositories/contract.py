from dataclasses import dataclass

import structlog
from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession

from prodik.application.interfaces.repositories import ContractRepository
from prodik.domain.contract.model import Contract

logger = structlog.get_logger()


@dataclass
class ContractRepositoryImpl(ContractRepository):
    session: AsyncSession

    async def create(self, contract: Contract) -> None:
        logger.debug("Repository create contract", contract_id=contract.id)

        await self.session.execute(
            insert(Contract).values(
                id=contract.id,
                company_a_id=contract.company_a_id,
                company_b_id=contract.company_b_id,
                company_a_offer_id=contract.company_a_offer_id,
                company_b_offer_id=contract.company_b_offer_id,
                company_a_role_id=contract.company_a_role_id,
                company_b_role_id=contract.company_b_role_id,
                status=contract.status,
                expires_in=contract.expires_in,
                created_at=contract.created_at,
                updated_at=contract.updated_at,
            ),
        )
