from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from uuid import uuid4

from conode.application.errors import (
    CannotTransferCompanyToCurrentOwnerError,
    EmailsOfAllParticipantsMustBeVerifiedError,
    TargetUserAccountCreatedTooRecentlyError,
)
from conode.application.interfaces.repositories import (
    CompanyRepository,
    UserGrantRepository,
    UserRepository,
)
from conode.application.interfaces.transaction_manager import TransactionManager
from conode.application.services import (
    AccessControlService,
    AuthorizationService,
    RoleManagmentService,
)
from conode.domain.company import CompanyId
from conode.domain.grant import UserGrant, UserGrantId
from conode.domain.user import UserId


@dataclass(frozen=True, slots=True, kw_only=True)
class TransferCompanyRequestDTO:
    target_user_id: UserId
    company_id: CompanyId


@dataclass
class TransferCompanyInteractor:
    user_repository: UserRepository
    access_control_service: AccessControlService
    authorization_service: AuthorizationService
    user_grant_repository: UserGrantRepository
    company_repository: CompanyRepository
    role_managment_service: RoleManagmentService
    transaction_manager: TransactionManager

    async def execute(self, request: TransferCompanyRequestDTO) -> None:
        async with self.transaction_manager:
            user = await self.authorization_service.get_authorized_user()
            if not user.email_verified:
                raise EmailsOfAllParticipantsMustBeVerifiedError(
                    "Emails of all participants must be verified", None
                )

            company = await self.company_repository.get_by_id(request.company_id)

            await self.access_control_service.ensure_user_can_manipulate_company(
                user, company
            )

            if request.target_user_id == user.id:
                raise CannotTransferCompanyToCurrentOwnerError(
                    "Cannot transfer company to current owner",
                    [{"key": "target_user_id", "value": request.target_user_id}],
                )

            target_user = await self.user_repository.get_by_id(request.target_user_id)
            if not target_user.email_verified:
                raise EmailsOfAllParticipantsMustBeVerifiedError(
                    "Emails of all participants must be verified", None
                )

            if target_user.created_at > datetime.now(UTC) - timedelta(days=1):
                raise TargetUserAccountCreatedTooRecentlyError(
                    "The target user account was created too recently", None
                )

            role = await self.user_grant_repository.revoke_company_owner_role_from_user(
                user, company
            )

            grant = UserGrant.new(
                user_grant_id=UserGrantId(uuid4()),
                role=role,
                user=target_user,
            )

            await self.user_grant_repository.create(grant)
