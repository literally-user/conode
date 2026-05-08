from http import HTTPStatus

from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter

from prodik.application.manage_node import CreateNodeInteractor, CreateNodeRequestDTO
from prodik.presentation.schemas.node import CreateNodeRequest, NodeSchema

router = APIRouter(tags=["nodes"], prefix="/nodes", route_class=DishkaRoute)


@router.post("/", status_code=HTTPStatus.CREATED)
async def create_node(
    request: CreateNodeRequest, interactor: FromDishka[CreateNodeInteractor]
) -> NodeSchema:
    result = await interactor.execute(
        CreateNodeRequestDTO(
            name=request.name,
            description=request.description,
            group_id=request.group_id,
        )
    )

    return NodeSchema(
        id=result.id,
        name=result.name.value,
        description=result.description.value,
        company_id=result.company_id,
    )
