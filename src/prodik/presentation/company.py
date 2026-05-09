from http import HTTPStatus

from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter

from prodik.application.manage_company import (
    RegisterCompanyInteractor,
    RegisterCompanyRequestDTO,
    VerifyCompanyInteractor,
)
from prodik.domain.company import CompanyId
from prodik.presentation.schemas.company import CompanySchema, RegisterCompanyRequest

router = APIRouter(tags=["companies"], prefix="/companies", route_class=DishkaRoute)


@router.post("/", status_code=HTTPStatus.CREATED)
async def register_company(
    request: RegisterCompanyRequest, interactor: FromDishka[RegisterCompanyInteractor]
) -> CompanySchema:
    company = await interactor.execute(
        RegisterCompanyRequestDTO(
            name=request.name,
            description=request.description,
        )
    )

    return CompanySchema(
        id=company.id,
        name=company.name.value,
        description=company.description.value,
        verified=company.verified,
        owner_id=company.owner_id,
        created_at=company.created_at,
        updated_at=company.updated_at,
    )


@router.patch("/{id}/verify", status_code=HTTPStatus.NO_CONTENT)
async def verify_company(
    id: CompanyId, interactor: FromDishka[VerifyCompanyInteractor]
) -> None:
    await interactor.execute(id)
