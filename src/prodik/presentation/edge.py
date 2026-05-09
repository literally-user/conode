from http import HTTPStatus

from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter

from prodik.application.manage_edges import (
    CreateEdgeInteractor,
    CreateEdgeRequestDTO,
    DecrementEdgeWeightInteractor,
    DeleteEdgeInteractor,
    IncrementEdgeWeightInteractor,
    UpdateEdgeWeightInteractor,
)
from prodik.domain.edge import EdgeId
from prodik.presentation.schemas.edge import (
    CreateEdgeRequest,
    EdgeSchema,
    UpdateEdgeWeightRequest,
)

router = APIRouter(tags=["edges"], prefix="/edges", route_class=DishkaRoute)


@router.post("/", status_code=HTTPStatus.CREATED)
async def create_edge(
    request: CreateEdgeRequest, interactor: FromDishka[CreateEdgeInteractor]
) -> EdgeSchema:
    result = await interactor.execute(
        CreateEdgeRequestDTO(
            node_a_id=request.node_a_id,
            node_b_id=request.node_b_id,
            context_id=request.context_id,
        )
    )
    return EdgeSchema(
        id=result.id,
        node_a_id=result.node_a_id,
        node_b_id=result.node_b_id,
        context_id=result.context_id,
        company_id=result.company_id,
        created_at=result.created_at,
        updated_at=result.updated_at,
    )


@router.delete("/{edge_id}", status_code=HTTPStatus.NO_CONTENT)
async def delete_edge(
    edge_id: EdgeId,
    interactor: FromDishka[DeleteEdgeInteractor],
) -> None:
    await interactor.execute(edge_id)


@router.patch("/{edge_id}/weight/increment", status_code=HTTPStatus.NO_CONTENT)
async def increment_edge_weight(
    edge_id: EdgeId,
    interactor: FromDishka[IncrementEdgeWeightInteractor],
) -> None:
    await interactor.execute(edge_id)


@router.patch("/{edge_id}/weight/decrement", status_code=HTTPStatus.NO_CONTENT)
async def decrement_edge_weight(
    edge_id: EdgeId,
    interactor: FromDishka[DecrementEdgeWeightInteractor],
) -> None:
    await interactor.execute(edge_id)


@router.patch("/{edge_id}/weight", status_code=HTTPStatus.NO_CONTENT)
async def update_edge_weight(
    edge_id: EdgeId,
    request: UpdateEdgeWeightRequest,
    interactor: FromDishka[UpdateEdgeWeightInteractor],
) -> None:
    await interactor.execute(edge_id, request.weight)
