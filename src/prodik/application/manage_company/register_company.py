from dataclasses import dataclass
from uuid import uuid7

from prodik.application.authorization.errors import InvalidCredentialsError
from prodik.application.interfaces.identity_provider import IdentityProvider
from prodik.application.interfaces.repositories import (
    CompanyRepository,
    SessionRepository,
    UserRepository,
)
from prodik.application.interfaces.transaction_manager import TransactionManager
from prodik.application.manage_company.errors import CompanyAlreadyExistsError
from prodik.application.services import AccessService
from prodik.domain.company import Company, CompanyId


@dataclass(frozen=True, slots=True, kw_only=True)
class RegisterCompanyRequest:
    name: str
    description: str


@dataclass
class RegisterCompanyInteractor:
    access_service: AccessService
    identity_provider: IdentityProvider
    company_repository: CompanyRepository
    transaction_manager: TransactionManager
    session_repository: SessionRepository
    user_repository: UserRepository

    async def execute(self, request: RegisterCompanyRequest) -> Company:
        async with self.transaction_manager:
            host = self.identity_provider.get_current_ip()
            user_id = self.identity_provider.get_current_user_id()

            session = await self.session_repository.get_by_host(host)
            if session is None:
                raise InvalidCredentialsError("Session not found", None)

            user = await self.user_repository.get_by_id(user_id)
            if user is None:
                raise InvalidCredentialsError("User not found", None)

            self.access_service.ensure_session_active(session, user)

            company = await self.company_repository.get_by_name(request.name)
            if company is not None:
                raise CompanyAlreadyExistsError(
                    "Company with this name already exists",
                    [{"key": "name", "value": request.name}],
                )

            company = Company.new(
                CompanyId(uuid7()),
                name=request.name,
                description=request.description,
                owner=user,
            )

            await self.company_repository.create(company)

            return company
