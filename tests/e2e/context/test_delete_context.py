from http import HTTPStatus

import pytest
from dirty_equals import IsPartialDict
from httpx import AsyncClient

from prodik.application.interfaces.repositories import ContextRepository
from tests.factories.common import authorization_headers
from tests.factories.models import CompanyFactory, ContextFactory, UserFactory


@pytest.mark.asyncio
async def test_delete_context_ok(
    transport: AsyncClient,
    user_factory: UserFactory,
    company_factory: CompanyFactory,
    context_factory: ContextFactory,
    context_repository: ContextRepository,
) -> None:
    user = await user_factory.build()
    company = await company_factory.build(owner=user.user)
    context = await context_factory.build(company=company)

    response = await transport.delete(
        f"/contexts/{context.id}",
        headers=authorization_headers(user.access_token),
    )

    contexts = await context_repository.get_all_by_company_id(company.id)

    assert len(contexts) == 0
    assert response.status_code == HTTPStatus.NO_CONTENT


@pytest.mark.asyncio
async def test_delete_context_user_without_correct_rights(
    transport: AsyncClient,
    user_factory: UserFactory,
    company_factory: CompanyFactory,
    context_factory: ContextFactory,
    context_repository: ContextRepository,
) -> None:
    users = (await user_factory.build(), await user_factory.build())
    company = await company_factory.build(owner=users[0].user)
    context = await context_factory.build(company=company)

    response = await transport.delete(
        f"/contexts/{context.id}",
        headers=authorization_headers(users[1].access_token),
    )

    contexts = await context_repository.get_all_by_company_id(company.id)

    assert len(contexts) == 1
    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == IsPartialDict(
        detail="Not enough rights to perform operation",
        meta=None,
    )
