from http import HTTPStatus

from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter

from prodik.application.manage_contexts import (
    CreateContextInteractor,
    CreateContextRequestDTO,
    DeleteContextInteractor,
)
from prodik.application.receive_context_info import (
    GetContextsByCurrentCompanyInteractor,
)
from prodik.domain.context import ContextId
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


@router.delete("/{context_id}", status_code=HTTPStatus.NO_CONTENT)
async def delete_context(
    context_id: ContextId, interactor: FromDishka[DeleteContextInteractor]
) -> None:
    await interactor.execute(context_id)


@router.get("/")
async def get_all_current_company_contexts(
    interactor: FromDishka[GetContextsByCurrentCompanyInteractor],
) -> list[ContextSchema]:
    result = await interactor.execute()

    return [
        ContextSchema(
            id=context.id,
            name=context.name.value,
            description=context.description.value,
            company_id=context.company_id,
            created_at=context.created_at,
            updated_at=context.updated_at,
        )
        for context in result
    ]
