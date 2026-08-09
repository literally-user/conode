from http import HTTPStatus

from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter

from conode.application.manage_company import (
    UpdateCompanyInteractor,
    UpdateCompanyRequestDTO,
)
from conode.application.register_company import (
    RegisterCompanyInteractor,
    RegisterCompanyRequestDTO,
)
from conode.application.verify_company import VerifyCompanyInteractor
from conode.domain.company import CompanyId
from conode.presentation.schemas.company import (
    CompanySchema,
    RegisterCompanyRequest,
    UpdateCompanyRequest,
)

router = APIRouter(tags=["companies"], prefix="/companies", route_class=DishkaRoute)


@router.post("/", status_code=HTTPStatus.CREATED)
async def register_company(
    request: RegisterCompanyRequest,
    interactor: FromDishka[RegisterCompanyInteractor],
) -> CompanySchema:
    company = await interactor.execute(
        RegisterCompanyRequestDTO(
            name=request.name,
            description=request.description,
        ),
    )

    return CompanySchema(
        id=company.id,
        name=company.name.value,
        description=company.description.value,
        verified=company.verified,
        owner_id=company.owner_id,
    )


@router.put("/{company_id}", status_code=HTTPStatus.NO_CONTENT)
async def update_company(
    company_id: CompanyId,
    request: UpdateCompanyRequest,
    interactor: FromDishka[UpdateCompanyInteractor],
) -> None:
    await interactor.execute(
        company_id,
        UpdateCompanyRequestDTO(name=request.name, description=request.description),
    )


@router.patch("/{company_id}/verify", status_code=HTTPStatus.NO_CONTENT)
async def verify_company(
    company_id: CompanyId,
    interactor: FromDishka[VerifyCompanyInteractor],
) -> None:
    await interactor.execute(company_id)
