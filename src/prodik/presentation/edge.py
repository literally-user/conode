from http import HTTPStatus

from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter

from prodik.application.manage_edges import CreateEdgeInteractor, CreateEdgeRequestDTO
from prodik.presentation.schemas.edge import CreateEdgeRequest, EdgeSchema

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
