from http import HTTPStatus

from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter

from prodik.application.manage_group import CreateGroupInteractor, CreateGroupRequestDTO
from prodik.presentation.schemas.group import CreateGroupRequest, GroupSchema

router = APIRouter(tags=["groups"], prefix="/groups", route_class=DishkaRoute)


@router.post("/", status_code=HTTPStatus.CREATED)
async def create_group(
    request: CreateGroupRequest, interactor: FromDishka[CreateGroupInteractor]
) -> GroupSchema:
    result = await interactor.execute(
        CreateGroupRequestDTO(
            name=request.name,
            description=request.description,
            parent_group_id=request.parent_group_id,
        )
    )

    return GroupSchema(
        id=result.id,
        name=result.name.value,
        description=result.description.value,
        company_id=result.company_id,
        parent_group_id=result.parent_group_id,
    )
