from http import HTTPStatus

from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter

from prodik.application.manage_role import (
    CreatePermissionRequestDTO,
    CreateRoleInteractor,
    CreateRoleRequestDTO,
    DeleteRoleInteractor,
    UpdatePermissionRequestDTO,
    UpdateRoleInteractor,
    UpdateRoleRequestDTO,
)
from prodik.domain.role import RoleId
from prodik.presentation.schemas.role import (
    CreateRoleRequest,
    PermissionSchema,
    RoleSchema,
    UpdateRoleRequest,
    UpdateRoleResponse,
)

router = APIRouter(prefix="/roles", route_class=DishkaRoute, tags=["roles"])


@router.post("/", status_code=HTTPStatus.CREATED)
async def create_role(
    request: CreateRoleRequest,
    interactor: FromDishka[CreateRoleInteractor],
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
        ),
    )

    return RoleSchema(
        id=result.id,
        owner_company_id=result.owner_company_id,
        name=result.name.value,
    )


@router.put("/{role_id}")
async def update_role(
    role_id: RoleId,
    request: UpdateRoleRequest,
    interactor: FromDishka[UpdateRoleInteractor],
) -> UpdateRoleResponse:
    result = await interactor.execute(
        UpdateRoleRequestDTO(
            name=request.name,
            role_id=role_id,
            permissions={
                permission_id: UpdatePermissionRequestDTO(
                    permission=value.permission,
                    entity_type=value.entity_type,
                    entity_id=value.entity_id,
                )
                for permission_id, value in request.permissions.items()
            },
        ),
    )

    return UpdateRoleResponse(
        role=RoleSchema(
            id=result.role.id,
            owner_company_id=result.role.owner_company_id,
            name=result.role.name.value,
        ),
        permissions=[
            PermissionSchema(
                id=permission.id,
                role_id=permission.role_id,
                permission=permission.permission,
                entity_type=permission.entity_type,
                entity_id=permission.entity_id,
            )
            for permission in result.permissions
        ],
    )


@router.delete("/{role_id}", status_code=HTTPStatus.NO_CONTENT)
async def delete_role(
    role_id: RoleId,
    interactor: FromDishka[DeleteRoleInteractor],
) -> None:
    await interactor.execute(role_id)
