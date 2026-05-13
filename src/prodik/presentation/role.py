from http import HTTPStatus

from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter

from prodik.application.manage_roles import (
    CreatePermissionRequestDTO,
    CreateRoleInteractor,
    CreateRoleRequestDTO,
)
from prodik.presentation.schemas.role import CreateRoleRequest, RoleSchema

router = APIRouter(prefix="/roles", route_class=DishkaRoute, tags=["roles"])


@router.post("/", status_code=HTTPStatus.CREATED)
async def create_role(
    request: CreateRoleRequest, interactor: FromDishka[CreateRoleInteractor]
) -> RoleSchema:
    result = await interactor.execute(
        CreateRoleRequestDTO(
            name=request.name,
            permissions=[
                CreatePermissionRequestDTO(
                    permission=permission.permission,
                    entity_id=permission.entity_id,
                    entity_type=permission.entity_type,
                )
                for permission in request.permissions
            ],
            company_id=request.company_id,
        )
    )

    return RoleSchema(
        id=result.id,
        owner_company_id=result.owner_company_id,
        name=result.name.value,
    )
