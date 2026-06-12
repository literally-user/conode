from http import HTTPStatus

from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter

from prodik.application.manage_context import (
    CreateContextInteractor,
    CreateContextRequestDTO,
    DeleteContextInteractor,
)
from prodik.domain.context import ContextId
from prodik.presentation.schemas.context import ContextSchema, CreateContextRequest

router = APIRouter(tags=["contexts"], prefix="/contexts", route_class=DishkaRoute)


@router.post("/", status_code=HTTPStatus.CREATED)
async def create_context(
    request: CreateContextRequest,
    interactor: FromDishka[CreateContextInteractor],
) -> ContextSchema:
    result = await interactor.execute(
        CreateContextRequestDTO(
            name=request.name,
            description=request.description,
            company_id=request.company_id,
        ),
    )
    return ContextSchema(
        id=result.id,
        name=result.name.value,
        description=result.description.value,
        company_id=result.company_id,
    )


@router.delete("/{context_id}", status_code=HTTPStatus.NO_CONTENT)
async def delete_context(
    context_id: ContextId,
    interactor: FromDishka[DeleteContextInteractor],
) -> None:
    await interactor.execute(context_id)
