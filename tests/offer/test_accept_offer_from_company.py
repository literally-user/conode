from http import HTTPStatus
from uuid import uuid4

import pytest
from dirty_equals import IsPartialDict
from httpx import AsyncClient

from tests.factories import (
    CompanyFactory,
    ContextFactory,
    GroupFactory,
    OfferFactory,
    UserFactory,
)


@pytest.mark.asyncio
async def test_accept_offer_ok(
    user_factory: UserFactory,
    company_factory: CompanyFactory,
    group_factory: GroupFactory,
    context_factory: ContextFactory,
    offer_factory: OfferFactory,
    test_client: AsyncClient,
) -> None:
    sender_response = await user_factory.create_user(admin=False)
    recipient_response = await user_factory.create_user(admin=False)
    from_company = await company_factory.create_company(user=sender_response.user)
    to_company = await company_factory.create_company(user=recipient_response.user)
    group = await group_factory.create_group(company=from_company)
    context = await context_factory.create_context(company=from_company)

    offer = await offer_factory.create_offer(
        from_company=from_company,
        to_company=to_company,
        groups={group.id: "READ"},
        contexts={context.id: "READ"},
    )

    response = await test_client.post(
        f"/offers/{offer.id}/accept",
        headers={"Authorization": f"Bearer {recipient_response.access_token}"},
    )

    assert response.status_code == HTTPStatus.NO_CONTENT


@pytest.mark.asyncio
async def test_accept_counter_offer_ok(
    user_factory: UserFactory,
    company_factory: CompanyFactory,
    group_factory: GroupFactory,
    context_factory: ContextFactory,
    offer_factory: OfferFactory,
    test_client: AsyncClient,
) -> None:
    sender_response = await user_factory.create_user(admin=False)
    recipient_response = await user_factory.create_user(admin=False)
    from_company = await company_factory.create_company(user=sender_response.user)
    to_company = await company_factory.create_company(user=recipient_response.user)
    group = await group_factory.create_group(company=from_company)
    context = await context_factory.create_context(company=from_company)

    original_offer = await offer_factory.create_offer(
        from_company=to_company,
        to_company=from_company,
        groups={group.id: "READ"},
        contexts={context.id: "READ"},
    )
    counter_offer = await offer_factory.create_counter_offer(
        from_company=from_company,
        to_company=to_company,
        from_offer=original_offer,
        groups={group.id: "MODIFY"},
        contexts={context.id: "MODIFY"},
    )

    response = await test_client.post(
        f"/offers/{counter_offer.id}/accept",
        headers={"Authorization": f"Bearer {recipient_response.access_token}"},
    )

    assert response.status_code == HTTPStatus.NO_CONTENT


@pytest.mark.asyncio
async def test_accept_offer_not_found(
    user_factory: UserFactory,
    test_client: AsyncClient,
) -> None:
    user_response = await user_factory.create_user(admin=False)
    fake_offer_id = uuid4()

    response = await test_client.post(
        f"/offers/{fake_offer_id}/accept",
        headers={"Authorization": f"Bearer {user_response.access_token}"},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == IsPartialDict(
        detail="Offer not found",
        meta=[{"key": "offer_id", "value": str(fake_offer_id)}],
    )


@pytest.mark.asyncio
async def test_accept_offer_forbidden(
    user_factory: UserFactory,
    company_factory: CompanyFactory,
    offer_factory: OfferFactory,
    test_client: AsyncClient,
) -> None:
    sender_response = await user_factory.create_user(admin=False)
    intruder_response = await user_factory.create_user(admin=False)
    from_company = await company_factory.create_company(user=sender_response.user)
    to_company = await company_factory.create_company()
    await company_factory.create_company(user=intruder_response.user)

    offer = await offer_factory.create_offer(
        from_company=from_company,
        to_company=to_company,
    )

    response = await test_client.post(
        f"/offers/{offer.id}/accept",
        headers={"Authorization": f"Bearer {intruder_response.access_token}"},
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == IsPartialDict(
        detail="Not enough rights to perform operation",
        meta=None,
    )
