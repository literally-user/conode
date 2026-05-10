from dataclasses import dataclass

from prodik.application.errors import CompanyNotFoundError
from prodik.application.interfaces.repositories import (
    CompanyRepository,
    ContextRepository,
)
from prodik.application.services import AccessControlService
from prodik.domain.context import Context


@dataclass
class GetContextsByCurrentCompanyInteractor:
    access_control_service: AccessControlService
    company_repository: CompanyRepository
    context_repository: ContextRepository

    async def execute(self) -> list[Context]:
        user = await self.access_control_service.get_authorized_user()

        company = await self.company_repository.get_by_user_id(user.id)
        if company is None:
            raise CompanyNotFoundError("Company not found", None)

        return await self.context_repository.get_all_by_company_id(company.id)
