from http import HTTPStatus

import pytest
from dirty_equals import IsPartialDataclass, IsPartialDict
from httpx import AsyncClient

from prodik.application.interfaces.repositories import ContextRepository
from prodik.domain.context import ContextDescription, ContextName
from tests.factories.common import authorization_headers
from tests.factories.models import CompanyFactory, UserFactory
from tests.factories.schemas import CreateContextRequestFactory


@pytest.mark.asyncio
async def test_create_context_ok(
    transport: AsyncClient,
    user_factory: UserFactory,
    company_factory: CompanyFactory,
    context_repository: ContextRepository,
) -> None:
    user = await user_factory.build()
    company = await company_factory.build(owner=user.user)

    request = CreateContextRequestFactory.build(company_id=company.id)

    response = await transport.post(
        "/contexts/",
        json=request.model_dump(mode="json"),
        headers=authorization_headers(user.access_token),
    )
    content = response.json()

    context = await context_repository.get_by_id(content["id"])

    assert response.status_code == HTTPStatus.CREATED
    assert context == IsPartialDataclass(
        name=ContextName(request.name),
        description=ContextDescription(request.description),
        company_id=company.id,
    )
    assert content == IsPartialDict(
        name=request.name, description=request.description, company_id=str(company.id)
    )


@pytest.mark.asyncio
async def test_create_context_user_without_correct_rights(
    transport: AsyncClient,
    user_factory: UserFactory,
    company_factory: CompanyFactory,
    context_repository: ContextRepository,
) -> None:
    users = (await user_factory.build(), await user_factory.build())
    company = await company_factory.build(owner=users[0].user)

    request = CreateContextRequestFactory.build(company_id=company.id)

    response = await transport.post(
        "/contexts/",
        json=request.model_dump(mode="json"),
        headers=authorization_headers(users[1].access_token),
    )

    contexts = await context_repository.get_all_by_company_id(company.id)

    assert len(contexts) == 0
    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == IsPartialDict(
        detail="Not enough rights to perform operation",
        meta=None,
    )
