from http import HTTPStatus
from typing import Final

import pytest
from dirty_equals import IsPartialDict, IsStr, IsUUID
from httpx import AsyncClient

from tests.factories import CompanyFactory, ContextFactory, UserFactory

EXPECTED_CONTEXTS_COUNT: Final = 2


@pytest.mark.asyncio
async def test_get_contexts_by_current_company_ok(
    test_client: AsyncClient,
    user_factory: UserFactory,
    company_factory: CompanyFactory,
    context_factory: ContextFactory,
) -> None:
    user = await user_factory.create_user(admin=False)
    company = await company_factory.create_company(user.user)
    context_1 = await context_factory.create_context(company=company)
    context_2 = await context_factory.create_context(company=company)

    response = await test_client.get(
        "/contexts/",
        headers={"Authorization": f"Bearer {user.access_token}"},
    )

    assert response.status_code == HTTPStatus.OK
    payload = response.json()
    assert len(payload) == EXPECTED_CONTEXTS_COUNT
    assert {item["id"] for item in payload} == {str(context_1.id), str(context_2.id)}
    for item in payload:
        assert item == IsPartialDict(
            id=IsUUID(),
            name=IsStr(),
            description=IsStr(),
            company_id=str(company.id),
        )


@pytest.mark.asyncio
async def test_get_contexts_by_current_company_not_found(
    test_client: AsyncClient,
    user_factory: UserFactory,
) -> None:
    user = await user_factory.create_user(admin=False)

    response = await test_client.get(
        "/contexts/",
        headers={"Authorization": f"Bearer {user.access_token}"},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == IsPartialDict(detail="Company not found", meta=None)
