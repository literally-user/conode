from typing import Protocol

from conode.domain.company import Company
from conode.domain.grant import UserGrant
from conode.domain.role import Role, RoleId
from conode.domain.user import User, UserId


class UserGrantRepository(Protocol):
    async def create(self, grant: UserGrant) -> None: ...
    async def delete(self, grant: UserGrant) -> None: ...
    async def get_all_by_user_id(self, user_id: UserId) -> list[UserGrant]: ...
    async def revoke_company_owner_role_from_user(
        self, user: User, company: Company
    ) -> Role: ...
    async def get_by_user_and_role_id(
        self,
        user_id: UserId,
        role_id: RoleId,
    ) -> UserGrant | None: ...
