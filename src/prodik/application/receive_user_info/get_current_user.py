from dataclasses import dataclass

from prodik.application.services import AccessControlService
from prodik.domain.user import User


@dataclass
class GetCurrentUserInteractor:
    access_control_service: AccessControlService

    async def execute(self) -> User:
        return await self.access_control_service.get_authorized_user()
