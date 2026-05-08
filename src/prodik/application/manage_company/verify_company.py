from dataclasses import dataclass

import structlog

from prodik.application.errors import (
    CompanyNotFoundError,
    NotEnoughRightsError,
    UserNotFoundError,
)
from prodik.application.interfaces.identity_provider import IdentityProvider
from prodik.application.interfaces.repositories import CompanyRepository, UserRepository
from prodik.application.interfaces.transaction_manager import TransactionManager
from prodik.domain.company import CompanyId

logger = structlog.get_logger()


@dataclass
class VerifyCompanyInteractor:
    transaction_manager: TransactionManager
    company_repository: CompanyRepository
    user_repository: UserRepository
    identity_provider: IdentityProvider

    async def execute(self, company_id: CompanyId) -> None:
        async with self.transaction_manager:
            user_meta = self.identity_provider.get_current_user_meta()

            logger.info("Received user meta")

            user = await self.user_repository.get_by_id(user_meta["user_id"])
            if user is None:
                raise UserNotFoundError("User not found", None)

            if not user.is_admin():
                raise NotEnoughRightsError(
                    "Not enough rights to perform operation", None
                )

            company = await self.company_repository.get_by_id(company_id)
            if company is None:
                raise CompanyNotFoundError("Company not found", None)

            company.verify()

            await self.company_repository.update(company)
