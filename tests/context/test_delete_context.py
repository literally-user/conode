from http import HTTPStatus

import pytest
from dirty_equals import IsPartialDict
from httpx import AsyncClient

from tests.factories import (
    CompanyFactory,
    ContextFactory,
    UserFactory,
)


@pytest.mark.asyncio
async def test_delete_context_ok(
    user_factory: UserFactory,
    company_factory: CompanyFactory,
    context_factory: ContextFactory,
    test_client: AsyncClient,
) -> None:
    user_factory_response = await user_factory.create_user(admin=False)
    company = await company_factory.create_company(user=user_factory_response.user)
    context = await context_factory.create_context(company)

    response = await test_client.delete(
        f"/contexts/{context.id}",
        headers={"Authorization": f"Bearer {user_factory_response.access_token}"},
    )

    assert response.status_code == HTTPStatus.NO_CONTENT


@pytest.mark.asyncio
async def test_delete_context_forbidden(
    user_factory: UserFactory,
    test_client: AsyncClient,
    context_factory: ContextFactory,
) -> None:
    context = await context_factory.create_context()

    user_factory_response = await user_factory.create_user()

    response = await test_client.delete(
        f"/contexts/{context.id}",
        headers={"Authorization": f"Bearer {user_factory_response.access_token}"},
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == IsPartialDict(
        detail="Not enough rights to perform operation",
        meta=None,
    )
