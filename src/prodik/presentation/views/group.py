from http import HTTPStatus

from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter

from prodik.application.manage_group import (
    CreateGroupInteractor,
    CreateGroupRequestDTO,
    DeleteGroupInteractor,
)
from prodik.domain.group import GroupId
from prodik.presentation.schemas.group import CreateGroupRequest, GroupSchema

router = APIRouter(tags=["groups"], prefix="/groups", route_class=DishkaRoute)


@router.post("/", status_code=HTTPStatus.CREATED)
async def create_group(
    request: CreateGroupRequest,
    interactor: FromDishka[CreateGroupInteractor],
) -> GroupSchema:
    result = await interactor.execute(
        CreateGroupRequestDTO(
            name=request.name,
            description=request.description,
            parent_group_id=request.parent_group_id,
            company_id=request.company_id,
        ),
    )

    return GroupSchema(
        id=result.id,
        name=result.name.value,
        description=result.description.value,
        company_id=result.company_id,
        parent_group_id=result.parent_group_id,
    )


@router.delete("/{group_id}", status_code=HTTPStatus.NO_CONTENT)
async def delete_group(
    group_id: GroupId,
    interactor: FromDishka[DeleteGroupInteractor],
) -> None:
    await interactor.execute(group_id)
