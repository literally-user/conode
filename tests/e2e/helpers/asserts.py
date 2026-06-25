from typing import Any

from prodik.application.interfaces.repositories import (
    CompanyRepository,
    RoleRepository,
    UserGrantRepository,
)
from prodik.domain.role import RoleName
from prodik.domain.user import User


async def assert_user_have_correct_rights(
    content: dict[str, Any],
    user: User,
    user_grant_repository: UserGrantRepository,
    company_repository: CompanyRepository,
    role_repository: RoleRepository,
) -> None:
    company = await company_repository.get_by_id(content["id"])
    role = await role_repository.get_by_name_and_company_id(
        RoleName("owner"), content["id"]
    )
    assert role is not None

    grant = await user_grant_repository.get_by_user_and_role_id(user.id, role.id)
    assert company is not None
    assert grant is not None
