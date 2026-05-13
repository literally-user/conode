from http import HTTPStatus
from uuid import uuid4

import pytest
from dirty_equals import IsPartialDict, IsStr
from httpx import AsyncClient

from tests.factories import (
    CompanyFactory,
    UserFactory,
    generate_random_string,
)


@pytest.mark.asyncio
async def test_create_context_ok(
    user_factory: UserFactory,
    company_factory: CompanyFactory,
    test_client: AsyncClient,
) -> None:
    user_factory_response = await user_factory.create_user(admin=False)
    company = await company_factory.create_company(user=user_factory_response.user)

    name = generate_random_string(10)
    description = generate_random_string(30)

    response = await test_client.post(
        "/contexts/",
        json={
            "name": name,
            "description": description,
            "company_id": str(company.id),
        },
        headers={"Authorization": f"Bearer {user_factory_response.access_token}"},
    )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == IsPartialDict(
        id=IsStr(),
        name=name,
        description=description,
        company_id=str(company.id),
    )


@pytest.mark.asyncio
async def test_create_context_company_not_found(
    user_factory: UserFactory,
    test_client: AsyncClient,
) -> None:
    user_factory_response = await user_factory.create_user(admin=False)

    response = await test_client.post(
        "/contexts/",
        json={
            "name": generate_random_string(10),
            "description": generate_random_string(30),
            "company_id": str(uuid4()),
        },
        headers={"Authorization": f"Bearer {user_factory_response.access_token}"},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == IsPartialDict(
        detail="Company not found",
        meta=None,
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
        json={
            "name": generate_random_string(5),
            "description": generate_random_string(30),
            "company_id": str(company.id),
        },
        headers={"Authorization": f"Bearer {user_factory_response.access_token}"},
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == IsPartialDict(
        detail="Not enough rights to perform operation", meta=None
    )
