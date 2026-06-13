from http import HTTPStatus

from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter

from prodik.application.attach_node_to_group import (
    AttachNodeInteractor,
    AttachNodeRequestDTO,
)
from prodik.application.detach_node_from_group import DetachNodeInteractor
from prodik.application.manage_node import (
    CreateNodeInteractor,
    CreateNodeRequestDTO,
    DeleteNodeInteractor,
)
from prodik.application.receive_graph_statistics import (
    GetNodeNeighboursInteractor,
    GetNodeNeighboursRequestDTO,
)
from prodik.application.receive_node_info import GetNodesByGroupInteractor
from prodik.application.update_node import (
    UpdateNodeInteractor,
    UpdateNodeRequestDTO,
)
from prodik.domain.context import ContextId
from prodik.domain.group import GroupId
from prodik.domain.node import NodeAssociationId, NodeId
from prodik.presentation.schemas.edge import EdgeSchema
from prodik.presentation.schemas.node import (
    AttachNodeRequest,
    CreateNodeRequest,
    NodeAssociationSchema,
    NodeSchema,
    UpdateNodeRequest,
)

router = APIRouter(tags=["nodes"], prefix="/nodes", route_class=DishkaRoute)


@router.post("/", status_code=HTTPStatus.CREATED)
async def create_node(
    request: CreateNodeRequest,
    interactor: FromDishka[CreateNodeInteractor],
) -> NodeSchema:
    result = await interactor.execute(
        CreateNodeRequestDTO(
            name=request.name,
            description=request.description,
            group_id=request.group_id,
        ),
    )

    return NodeSchema(
        id=result.id,
        name=result.name.value,
        description=result.description.value,
        company_id=result.company_id,
    )


@router.get("/{node_id}/neighbours")
async def get_neighbours(
    node_id: NodeId,
    context_id: ContextId,
    interactor: FromDishka[GetNodeNeighboursInteractor],
) -> list[tuple[NodeSchema, EdgeSchema]]:
    result = await interactor.execute(
        GetNodeNeighboursRequestDTO(
            node_id=node_id,
            context_id=context_id,
        )
    )

    return [
        (
            NodeSchema(
                id=node.id,
                name=node.name.value,
                description=node.description.value,
                company_id=node.company_id,
            ),
            EdgeSchema(
                id=edge.id,
                node_a_id=edge.node_a_id,
                node_b_id=edge.node_b_id,
                context_id=edge.context_id,
                company_id=edge.company_id,
            ),
        )
        for node, edge in result
    ]


@router.put("/{node_id}")
async def update_node(
    node_id: NodeId,
    request: UpdateNodeRequest,
    interactor: FromDishka[UpdateNodeInteractor],
) -> NodeSchema:
    result = await interactor.execute(
        UpdateNodeRequestDTO(
            name=request.name,
            description=request.description,
            node_id=node_id,
        ),
    )

    return NodeSchema(
        id=result.id,
        name=result.name.value,
        description=result.description.value,
        company_id=result.company_id,
    )


@router.delete("/{node_id}", status_code=HTTPStatus.NO_CONTENT)
async def delete_node(
    node_id: NodeId,
    interactor: FromDishka[DeleteNodeInteractor],
) -> None:
    await interactor.execute(node_id)


@router.post("/attach", status_code=HTTPStatus.CREATED)
async def attach_nodes(
    request: AttachNodeRequest,
    interactor: FromDishka[AttachNodeInteractor],
) -> list[NodeAssociationSchema]:
    result = await interactor.execute(
        AttachNodeRequestDTO(group_id=request.group_id, nodes=request.nodes),
    )

    return [
        NodeAssociationSchema(
            id=association.id,
            node_id=association.node_id,
            group_id=association.group_id,
        )
        for association in result
    ]


@router.delete("/association/{association_id}", status_code=HTTPStatus.NO_CONTENT)
async def detach_node(
    association_id: NodeAssociationId,
    interactor: FromDishka[DetachNodeInteractor],
) -> None:
    await interactor.execute(association_id)


@router.get("/{group_id}")
async def get_all_nodes_by_group(
    group_id: GroupId,
    interactor: FromDishka[GetNodesByGroupInteractor],
) -> list[NodeSchema]:
    result = await interactor.execute(group_id)
    return [
        NodeSchema(
            id=node.id,
            name=node.name.value,
            description=node.description.value,
            company_id=node.company_id,
        )
        for node in result
    ]
