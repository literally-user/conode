from http import HTTPStatus

from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter

from prodik.application.manage_association import (
    AttachNodeInteractor,
    AttachNodeRequestDTO,
    DetachNodeInteractor,
)
from prodik.application.manage_node import CreateNodeInteractor, CreateNodeRequestDTO
from prodik.domain.node import NodeAssociationId
from prodik.presentation.schemas.node import (
    AttachNodeRequest,
    CreateNodeRequest,
    NodeAssociationSchema,
    NodeSchema,
)

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


@router.post("/attach", status_code=HTTPStatus.CREATED)
async def attach_nodes(
    request: AttachNodeRequest, interactor: FromDishka[AttachNodeInteractor]
) -> list[NodeAssociationSchema]:
    result = await interactor.execute(
        AttachNodeRequestDTO(group_id=request.group_id, nodes=request.nodes)
    )

    return [
        NodeAssociationSchema(
            id=association.id,
            node_id=association.node_id,
            group_id=association.group_id,
        )
        for association in result
    ]


@router.delete("/attach/{association_id}", status_code=HTTPStatus.NO_CONTENT)
async def detach_node(
    association_id: NodeAssociationId,
    interactor: FromDishka[DetachNodeInteractor],
) -> None:
    await interactor.execute(association_id)
