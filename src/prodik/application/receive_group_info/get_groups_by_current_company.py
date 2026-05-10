from dataclasses import dataclass

from prodik.application.errors import CompanyNotFoundError
from prodik.application.interfaces.repositories import (
    CompanyRepository,
    GroupRepository,
)
from prodik.application.services import AccessControlService
from prodik.domain.group import Group


@dataclass
class GetGroupsByCurrentCompanyInteractor:
    access_control_service: AccessControlService
    company_repository: CompanyRepository
    group_repository: GroupRepository

    async def execute(self) -> list[Group]:
        user = await self.access_control_service.get_authorized_user()

        company = await self.company_repository.get_by_user_id(user.id)
        if company is None:
            raise CompanyNotFoundError("Company not found", None)

        return await self.group_repository.get_all_by_company_id(company.id)
