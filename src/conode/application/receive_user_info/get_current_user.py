from dataclasses import dataclass

from conode.application.services import AuthorizationService
from conode.domain.user import User


@dataclass
class GetCurrentUserInteractor:
    authorization_service: AuthorizationService

    async def execute(self) -> User:
        return await self.authorization_service.get_authorized_user()
