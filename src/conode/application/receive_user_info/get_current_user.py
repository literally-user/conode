from dataclasses import dataclass

from conode.application.services import AccessControlService
from conode.domain.user import User


@dataclass
class GetCurrentUserInteractor:
    access_control_service: AccessControlService

    async def execute(self) -> User:
        return await self.access_control_service.get_authorized_user()
