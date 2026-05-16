from http import HTTPStatus

from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter

from prodik.application.share_graph import (
    AcceptOfferInteractor,
    DeclineOfferInteractor,
    SendOfferToCompanyInteractor,
    SendOfferToCompanyRequestDTO,
)
from prodik.domain.offer import OfferId
from prodik.presentation.schemas.offer import OfferSchema, SendOfferToCompanyRequest

router = APIRouter(tags=["offers"], prefix="/offers", route_class=DishkaRoute)


@router.post("/")
async def send_offer(
    request: SendOfferToCompanyRequest,
    interactor: FromDishka[SendOfferToCompanyInteractor],
) -> OfferSchema:
    result = await interactor.execute(
        SendOfferToCompanyRequestDTO(
            title=request.title,
            description=request.description,
            from_company_id=request.from_company_id,
            to_company_id=request.to_company_id,
            requires_counteroffer=request.requires_counteroffer,
            from_offer_id=request.from_offer_id,
            groups=request.groups,
            contexts=request.contexts,
            expires_in=request.expires_in,
        ),
    )

    return OfferSchema(
        id=result.id,
        title=result.title.value,
        description=result.description.value,
        status=result.status,
        from_company_id=result.from_company_id,
        to_company_id=result.to_company_id,
        from_offer=result.from_offer,
        requires_counteroffer=result.requires_counteroffer,
        expires_in=result.expires_in,
    )


@router.post("/{offer_id}/accept", status_code=HTTPStatus.NO_CONTENT)
async def accept_offer(
    offer_id: OfferId,
    interactor: FromDishka[AcceptOfferInteractor],
) -> None:
    await interactor.execute(offer_id)


@router.post("/{offer_id}/decline", status_code=HTTPStatus.NO_CONTENT)
async def decline_offer(
    offer_id: OfferId,
    interactor: FromDishka[DeclineOfferInteractor],
) -> None:
    await interactor.execute(offer_id)
