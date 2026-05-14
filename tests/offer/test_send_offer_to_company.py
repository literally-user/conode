from datetime import UTC, datetime, timedelta
from http import HTTPStatus
from uuid import uuid4

import pytest
from dirty_equals import IsPartialDict, IsStr
from httpx import AsyncClient

from tests.factories import (
    CompanyFactory,
    ContextFactory,
    GroupFactory,
    OfferFactory,
    UserFactory,
)


def _expires_in() -> str:
    return (datetime.now(UTC) + timedelta(days=7)).isoformat()


@pytest.mark.asyncio
async def test_send_offer_ok(
    user_factory: UserFactory,
    company_factory: CompanyFactory,
    group_factory: GroupFactory,
    context_factory: ContextFactory,
    test_client: AsyncClient,
) -> None:
    sender_response = await user_factory.create_user(admin=False)
    from_company = await company_factory.create_company(user=sender_response.user)
    to_company = await company_factory.create_company()
    group = await group_factory.create_group(company=from_company)
    context = await context_factory.create_context(company=from_company)

    response = await test_client.post(
        "/offers/",
        json={
            "title": "Test Offer",
            "description": "Test description",
            "from_company_id": str(from_company.id),
            "to_company_id": str(to_company.id),
            "requires_counteroffer": False,
            "from_offer_id": None,
            "groups": {str(group.id): "READ"},
            "contexts": {str(context.id): "READ"},
            "expires_in": _expires_in(),
        },
        headers={"Authorization": f"Bearer {sender_response.access_token}"},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == IsPartialDict(
        id=IsStr(),
        title="Test Offer",
        description="Test description",
        status="PENDING",
        from_company_id=str(from_company.id),
        to_company_id=str(to_company.id),
        from_offer=None,
        requires_counteroffer=False,
    )


@pytest.mark.asyncio
async def test_send_offer_as_counteroffer_ok(
    user_factory: UserFactory,
    company_factory: CompanyFactory,
    group_factory: GroupFactory,
    context_factory: ContextFactory,
    offer_factory: OfferFactory,
    test_client: AsyncClient,
) -> None:
    sender_response = await user_factory.create_user(admin=False)
    from_company = await company_factory.create_company(user=sender_response.user)
    to_company = await company_factory.create_company()
    group = await group_factory.create_group(company=from_company)
    context = await context_factory.create_context(company=from_company)

    original_offer = await offer_factory.create_offer(
        from_company=to_company,
        to_company=from_company,
    )

    response = await test_client.post(
        "/offers/",
        json={
            "title": "Counter Offer",
            "description": "Counter description",
            "from_company_id": str(from_company.id),
            "to_company_id": str(to_company.id),
            "requires_counteroffer": False,
            "from_offer_id": str(original_offer.id),
            "groups": {str(group.id): "READ"},
            "contexts": {str(context.id): "MODIFY"},
            "expires_in": _expires_in(),
        },
        headers={"Authorization": f"Bearer {sender_response.access_token}"},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == IsPartialDict(
        status="PENDING",
        from_company_id=str(from_company.id),
        to_company_id=str(to_company.id),
        from_offer=str(original_offer.id),
    )


@pytest.mark.asyncio
async def test_send_offer_from_company_not_found(
    user_factory: UserFactory,
    company_factory: CompanyFactory,
    test_client: AsyncClient,
) -> None:
    sender_response = await user_factory.create_user(admin=False)
    to_company = await company_factory.create_company()
    fake_company_id = str(uuid4())

    response = await test_client.post(
        "/offers/",
        json={
            "title": "Test Offer",
            "description": "Test description",
            "from_company_id": fake_company_id,
            "to_company_id": str(to_company.id),
            "requires_counteroffer": False,
            "from_offer_id": None,
            "groups": {},
            "contexts": {},
            "expires_in": _expires_in(),
        },
        headers={"Authorization": f"Bearer {sender_response.access_token}"},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == IsPartialDict(detail="Company not found", meta=None)


@pytest.mark.asyncio
async def test_send_offer_to_company_not_found(
    user_factory: UserFactory,
    company_factory: CompanyFactory,
    test_client: AsyncClient,
) -> None:
    sender_response = await user_factory.create_user(admin=False)
    from_company = await company_factory.create_company(user=sender_response.user)
    fake_company_id = str(uuid4())

    response = await test_client.post(
        "/offers/",
        json={
            "title": "Test Offer",
            "description": "Test description",
            "from_company_id": str(from_company.id),
            "to_company_id": fake_company_id,
            "requires_counteroffer": False,
            "from_offer_id": None,
            "groups": {},
            "contexts": {},
            "expires_in": _expires_in(),
        },
        headers={"Authorization": f"Bearer {sender_response.access_token}"},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == IsPartialDict(detail="Company not found", meta=None)


@pytest.mark.asyncio
async def test_send_offer_forbidden(
    user_factory: UserFactory,
    company_factory: CompanyFactory,
    test_client: AsyncClient,
) -> None:
    sender_response = await user_factory.create_user(admin=False)
    another_company = await company_factory.create_company()
    to_company = await company_factory.create_company()

    response = await test_client.post(
        "/offers/",
        json={
            "title": "Test Offer",
            "description": "Test description",
            "from_company_id": str(another_company.id),
            "to_company_id": str(to_company.id),
            "requires_counteroffer": False,
            "from_offer_id": None,
            "groups": {},
            "contexts": {},
            "expires_in": _expires_in(),
        },
        headers={"Authorization": f"Bearer {sender_response.access_token}"},
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == IsPartialDict(
        detail="Not enough rights to perform operation", meta=None
    )


@pytest.mark.asyncio
async def test_send_offer_group_not_found(
    user_factory: UserFactory,
    company_factory: CompanyFactory,
    test_client: AsyncClient,
) -> None:
    sender_response = await user_factory.create_user(admin=False)
    from_company = await company_factory.create_company(user=sender_response.user)
    to_company = await company_factory.create_company()

    response = await test_client.post(
        "/offers/",
        json={
            "title": "Test Offer",
            "description": "Test description",
            "from_company_id": str(from_company.id),
            "to_company_id": str(to_company.id),
            "requires_counteroffer": False,
            "from_offer_id": None,
            "groups": {str(uuid4()): "READ"},
            "contexts": {},
            "expires_in": _expires_in(),
        },
        headers={"Authorization": f"Bearer {sender_response.access_token}"},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == IsPartialDict(
        detail="Some of groups not found", meta=None
    )


@pytest.mark.asyncio
async def test_send_offer_context_not_found(
    user_factory: UserFactory,
    company_factory: CompanyFactory,
    test_client: AsyncClient,
) -> None:
    sender_response = await user_factory.create_user(admin=False)
    from_company = await company_factory.create_company(user=sender_response.user)
    to_company = await company_factory.create_company()

    response = await test_client.post(
        "/offers/",
        json={
            "title": "Test Offer",
            "description": "Test description",
            "from_company_id": str(from_company.id),
            "to_company_id": str(to_company.id),
            "requires_counteroffer": False,
            "from_offer_id": None,
            "groups": {},
            "contexts": {str(uuid4()): "READ"},
            "expires_in": _expires_in(),
        },
        headers={"Authorization": f"Bearer {sender_response.access_token}"},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == IsPartialDict(
        detail="Some of contexts not found", meta=None
    )


@pytest.mark.asyncio
async def test_send_offer_from_offer_not_found(
    user_factory: UserFactory,
    company_factory: CompanyFactory,
    test_client: AsyncClient,
) -> None:
    sender_response = await user_factory.create_user(admin=False)
    from_company = await company_factory.create_company(user=sender_response.user)
    to_company = await company_factory.create_company()

    response = await test_client.post(
        "/offers/",
        json={
            "title": "Test Offer",
            "description": "Test description",
            "from_company_id": str(from_company.id),
            "to_company_id": str(to_company.id),
            "requires_counteroffer": False,
            "from_offer_id": str(uuid4()),
            "groups": {},
            "contexts": {},
            "expires_in": _expires_in(),
        },
        headers={"Authorization": f"Bearer {sender_response.access_token}"},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == IsPartialDict(detail="Offer not found", meta=None)
