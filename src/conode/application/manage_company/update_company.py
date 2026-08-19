from dataclasses import dataclass

from conode.application.interfaces.repositories import CompanyRepository
from conode.application.interfaces.transaction_manager import TransactionManager
from conode.application.services import AccessControlService, AuthorizationService
from conode.domain.company import CompanyId


@dataclass(slots=True, kw_only=True, frozen=True)
class UpdateCompanyRequestDTO:
    description: str
    name: str


@dataclass
class UpdateCompanyInteractor:
    transaction_manager: TransactionManager
    access_control_service: AccessControlService
    authorization_service: AuthorizationService
    company_repository: CompanyRepository

    async def execute(
        self, company_id: CompanyId, request: UpdateCompanyRequestDTO
    ) -> None:
        async with self.transaction_manager:
            user = await self.authorization_service.get_authorized_user()
            company = await self.company_repository.get_by_id(company_id)

            await self.access_control_service.ensure_user_can_manipulate_company(
                user, company
            )

            company.update(
                name=request.name,
                description=request.description,
            )

            await self.company_repository.update(company)
