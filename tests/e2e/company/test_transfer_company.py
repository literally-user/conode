from datetime import timedelta
from http import HTTPStatus

import pytest
from httpx import AsyncClient

from conode.application.interfaces.repositories import RoleRepository
from conode.domain.role import OWNER_COMPANY_ROLE_NAME
from tests.factories.common import authorization_headers
from tests.factories.models import CompanyFactory, UserFactory
from tests.factories.schemas import TransferCompanyRequestFactory


@pytest.mark.asyncio
async def test_transfer_company_ok(
    transport: AsyncClient,
    user_factory: UserFactory,
    company_factory: CompanyFactory,
    role_repository: RoleRepository,
) -> None:
    users = (
        await user_factory.build(verified=True),
        await user_factory.build(verified=True, timedelta_ago=timedelta(days=1)),
    )
    company = await company_factory.build(owner=users[0].user)

    request = TransferCompanyRequestFactory.build(
        target_user_id=users[1].user.id,
        company_id=company.id,
    )

    response = await transport.post(
        "/companies/transfer",
        json=request.model_dump(mode="json"),
        headers=authorization_headers(users[0].access_token),
    )

    caller_user_roles = await role_repository.get_all_by_user_id(users[0].user.id)
    target_user_roles = await role_repository.get_all_by_user_id(users[1].user.id)

    assert response.status_code == HTTPStatus.NO_CONTENT
    assert not any(
        role.name == OWNER_COMPANY_ROLE_NAME and role.owner_company_id == company.id
        for role in caller_user_roles
    )
    assert any(
        role.name == OWNER_COMPANY_ROLE_NAME and role.owner_company_id == company.id
        for role in target_user_roles
    )


@pytest.mark.asyncio
async def test_transfer_company_account_created_too_recently(
    transport: AsyncClient,
    user_factory: UserFactory,
    company_factory: CompanyFactory,
    role_repository: RoleRepository,
) -> None:
    users = (
        await user_factory.build(verified=True),
        await user_factory.build(verified=True),
    )
    company = await company_factory.build(owner=users[0].user)

    request = TransferCompanyRequestFactory.build(
        target_user_id=users[1].user.id,
        company_id=company.id,
    )

    response = await transport.post(
        "/companies/transfer",
        json=request.model_dump(mode="json"),
        headers=authorization_headers(users[0].access_token),
    )

    caller_user_roles = await role_repository.get_all_by_user_id(users[0].user.id)
    target_user_roles = await role_repository.get_all_by_user_id(users[1].user.id)

    assert response.status_code == HTTPStatus.UNPROCESSABLE_CONTENT
    assert any(
        role.name == OWNER_COMPANY_ROLE_NAME and role.owner_company_id == company.id
        for role in caller_user_roles
    )
    assert not any(
        role.name == OWNER_COMPANY_ROLE_NAME and role.owner_company_id == company.id
        for role in target_user_roles
    )


@pytest.mark.asyncio
async def test_transfer_company_target_user_email_not_verified(
    transport: AsyncClient,
    user_factory: UserFactory,
    company_factory: CompanyFactory,
    role_repository: RoleRepository,
) -> None:
    users = (
        await user_factory.build(verified=True),
        await user_factory.build(verified=False),
    )
    company = await company_factory.build(owner=users[0].user)

    request = TransferCompanyRequestFactory.build(
        target_user_id=users[1].user.id,
        company_id=company.id,
    )

    response = await transport.post(
        "/companies/transfer",
        json=request.model_dump(mode="json"),
        headers=authorization_headers(users[0].access_token),
    )

    caller_user_roles = await role_repository.get_all_by_user_id(users[0].user.id)
    target_user_roles = await role_repository.get_all_by_user_id(users[1].user.id)

    assert response.status_code == HTTPStatus.UNPROCESSABLE_CONTENT
    assert any(
        role.name == OWNER_COMPANY_ROLE_NAME and role.owner_company_id == company.id
        for role in caller_user_roles
    )
    assert not any(
        role.name == OWNER_COMPANY_ROLE_NAME and role.owner_company_id == company.id
        for role in target_user_roles
    )


@pytest.mark.asyncio
async def test_transfer_company_caller_user_email_not_verified(
    transport: AsyncClient,
    user_factory: UserFactory,
    company_factory: CompanyFactory,
    role_repository: RoleRepository,
) -> None:
    users = (
        await user_factory.build(verified=False),
        await user_factory.build(verified=True),
    )
    company = await company_factory.build(owner=users[0].user)

    request = TransferCompanyRequestFactory.build(
        target_user_id=users[1].user.id,
        company_id=company.id,
    )

    response = await transport.post(
        "/companies/transfer",
        json=request.model_dump(mode="json"),
        headers=authorization_headers(users[0].access_token),
    )

    caller_user_roles = await role_repository.get_all_by_user_id(users[0].user.id)
    target_user_roles = await role_repository.get_all_by_user_id(users[1].user.id)

    assert response.status_code == HTTPStatus.UNPROCESSABLE_CONTENT
    assert any(
        role.name == OWNER_COMPANY_ROLE_NAME and role.owner_company_id == company.id
        for role in caller_user_roles
    )
    assert not any(
        role.name == OWNER_COMPANY_ROLE_NAME and role.owner_company_id == company.id
        for role in target_user_roles
    )
