from http import HTTPStatus

from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter

from conode.application.manage_profile import (
    UpdateCurrentUserProfileInteractor,
    UpdateCurrentUserProfileRequestDTO,
    UpdateUserProfileInteractor,
    UpdateUserProfileRequestDTO,
)
from conode.application.manage_user_rights import (
    GiveRoleToUserInteractor,
    RevokeRoleFromUserInteractor,
)
from conode.application.receive_user_info import (
    GetCurrentUserInteractor,
    GetUserByUsernameInteractor,
)
from conode.domain.role import RoleId
from conode.domain.user import UserId
from conode.presentation.schemas.user import (
    UpdateCurrentUserProfileRequest,
    UpdateUserProfileRequest,
    UserSchema,
)

router = APIRouter(tags=["users"], route_class=DishkaRoute, prefix="/users")


@router.put("/me/profile", status_code=HTTPStatus.NO_CONTENT)
async def update_current_user_profile(
    request: UpdateCurrentUserProfileRequest,
    interactor: FromDishka[UpdateCurrentUserProfileInteractor],
) -> None:
    await interactor.execute(
        UpdateCurrentUserProfileRequestDTO(
            username=request.username,
            first_name=request.first_name,
            last_name=request.last_name,
            bio=request.bio,
        ),
    )


@router.put("/me/profile/{user_id}", status_code=HTTPStatus.NO_CONTENT)
async def update_user_profile(
    user_id: UserId,
    request: UpdateUserProfileRequest,
    interactor: FromDishka[UpdateUserProfileInteractor],
) -> None:
    await interactor.execute(
        user_id,
        UpdateUserProfileRequestDTO(
            username=request.username,
            first_name=request.first_name,
            last_name=request.last_name,
            bio=request.bio,
        ),
    )


@router.get("/me/profile")
async def get_current_user_profile(
    interactor: FromDishka[GetCurrentUserInteractor],
) -> UserSchema:
    result = await interactor.execute()
    return UserSchema(
        id=result.id,
        username=result.username.value,
        first_name=result.first_name.value,
        last_name=result.last_name.value,
        email=result.email.value,
        bio=result.bio.value,
    )


@router.get("/{username}")
async def get_user_by_username(
    username: str,
    interactor: FromDishka[GetUserByUsernameInteractor],
) -> UserSchema:
    result = await interactor.execute(username)

    return UserSchema(
        id=result.id,
        username=result.username.value,
        first_name=result.first_name.value,
        last_name=result.last_name.value,
        email=result.email.value,
        bio=result.bio.value,
    )


@router.post("/{user_id}/roles/{role_id}")
async def give_role_to_user(
    user_id: UserId,
    role_id: RoleId,
    interactor: FromDishka[GiveRoleToUserInteractor],
) -> None:
    await interactor.execute(user_id=user_id, role_id=role_id)


@router.delete("/{user_id}/roles/{role_id}")
async def revoke_role_from_user(
    user_id: UserId,
    role_id: RoleId,
    interactor: FromDishka[RevokeRoleFromUserInteractor],
) -> None:
    await interactor.execute(user_id=user_id, role_id=role_id)
