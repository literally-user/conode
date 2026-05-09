from http import HTTPStatus

from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter

from prodik.application.manage_contexts import (
    CreateContextInteractor,
    CreateContextRequestDTO,
)
from prodik.presentation.schemas.context import ContextSchema, CreateContextRequest

router = APIRouter(tags=["contexts"], prefix="/contexts", route_class=DishkaRoute)


@router.post("/", status_code=HTTPStatus.CREATED)
async def create_context(
    request: CreateContextRequest, interactor: FromDishka[CreateContextInteractor]
) -> ContextSchema:
    result = await interactor.execute(
        CreateContextRequestDTO(name=request.name, description=request.description)
    )
    return ContextSchema(
        id=result.id,
        name=result.name.value,
        description=result.description.value,
        company_id=result.company_id,
        created_at=result.created_at,
        updated_at=result.updated_at,
    )
