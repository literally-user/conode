from dataclasses import dataclass

from prodik.application.errors import (
    CompanyNotFoundError,
    NotEnoughRightsError,
)
from prodik.application.interfaces.repositories import CompanyRepository
from prodik.application.interfaces.transaction_manager import TransactionManager
from prodik.application.services import AccessControlService
from prodik.domain.company import CompanyId


@dataclass
class VerifyCompanyInteractor:
    transaction_manager: TransactionManager
    company_repository: CompanyRepository
    access_control_service: AccessControlService

    async def execute(self, company_id: CompanyId) -> None:
        async with self.transaction_manager:
            user = await self.access_control_service.get_authorized_user()

            if not user.is_admin():
                raise NotEnoughRightsError(
                    "Not enough rights to perform operation",
                    [{"key": "user_id", "value": user.id}],
                )

            company = await self.company_repository.get_by_id(company_id)
            if company is None:
                raise CompanyNotFoundError(
                    "Company not found",
                    [{"key": "company_id", "value": company_id}],
                )

            company.verify()

            await self.company_repository.update(company)
