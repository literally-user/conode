from http import HTTPStatus
from uuid import uuid4

import pytest
from dirty_equals import IsPartialDict, IsStr
from httpx import AsyncClient

from tests.factories import (
    CompanyFactory,
    CreateContextRequestFactory,
    UserFactory,
)


@pytest.mark.asyncio
async def test_create_context_ok(
    user_factory: UserFactory,
    company_factory: CompanyFactory,
    test_client: AsyncClient,
) -> None:
    user_factory_response = await user_factory.create_user(admin=False)
    company = await company_factory.create_company(user=user_factory_response.user)

    request = CreateContextRequestFactory.build(
        company_id=company.id,
    )

    response = await test_client.post(
        "/contexts/",
        json=request.model_dump(mode="json"),
        headers={"Authorization": f"Bearer {user_factory_response.access_token}"},
    )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == IsPartialDict(
        id=IsStr(),
        name=request.name,
        description=request.description,
        company_id=str(company.id),
    )


@pytest.mark.asyncio
async def test_create_context_company_not_found(
    user_factory: UserFactory,
    test_client: AsyncClient,
) -> None:
    user_factory_response = await user_factory.create_user(admin=False)
    fake_company_id = uuid4()

    response = await test_client.post(
        "/contexts/",
        json=CreateContextRequestFactory.build(
            company_id=fake_company_id,
        ).model_dump(mode="json"),
        headers={"Authorization": f"Bearer {user_factory_response.access_token}"},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == IsPartialDict(
        detail="Company not found",
        meta=[{"key": "company_id", "value": str(fake_company_id)}],
    )


@pytest.mark.asyncio
async def test_create_context_forbidden(
    user_factory: UserFactory,
    company_factory: CompanyFactory,
    test_client: AsyncClient,
) -> None:
    company = await company_factory.create_company()

    user_factory_response = await user_factory.create_user()

    response = await test_client.post(
        "/contexts/",
        json=CreateContextRequestFactory.build(
            name="abcde",
            company_id=company.id,
        ).model_dump(mode="json"),
        headers={"Authorization": f"Bearer {user_factory_response.access_token}"},
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == IsPartialDict(
        detail="Not enough rights to perform operation",
        meta=None,
    )
