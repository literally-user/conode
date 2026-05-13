from http import HTTPStatus

from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter

from prodik.application.give_role_to_user import GiveRoleToUserInteractor
from prodik.application.manage_credentials import (
    UpdateCurrentUserPasswordInteractor,
    UpdateCurrentUserPasswordRequestDTO,
)
from prodik.application.manage_profile import (
    UpdateCurrentUserProfileInteractor,
    UpdateCurrentUserProfileRequestDTO,
)
from prodik.application.receive_user_info import (
    GetCurrentUserInteractor,
    GetUserByUsernameInteractor,
)
from prodik.application.revoke_role_from_user import RevokeRoleFromUserInteractor
from prodik.domain.role import RoleId
from prodik.domain.user import UserId
from prodik.presentation.schemas.auth import AuthResponse
from prodik.presentation.schemas.user import (
    UpdateCurrentUserPasswordRequest,
    UpdateCurrentUserProfileRequest,
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
            email=request.email,
            bio=request.bio,
        )
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


@router.put("/me/password")
async def update_current_user_password(
    request: UpdateCurrentUserPasswordRequest,
    interactor: FromDishka[UpdateCurrentUserPasswordInteractor],
) -> AuthResponse:
    result = await interactor.execute(
        UpdateCurrentUserPasswordRequestDTO(
            old_password=request.old_password, new_password=request.new_password
        )
    )
    return AuthResponse(
        access_token=result.access_token,
        refresh_token=result.access_token,
        expires_in=result.expires_in,
    )


@router.get("/{username}")
async def get_user_by_username(
    username: str, interactor: FromDishka[GetUserByUsernameInteractor]
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
    user_id: UserId, role_id: RoleId, interactor: FromDishka[GiveRoleToUserInteractor]
) -> None:
    await interactor.execute(user_id=user_id, role_id=role_id)


@router.delete("/{user_id}/roles/{role_id}")
async def revoke_role_from_user(
    user_id: UserId,
    role_id: RoleId,
    interactor: FromDishka[RevokeRoleFromUserInteractor],
) -> None:
    await interactor.execute(user_id=user_id, role_id=role_id)
