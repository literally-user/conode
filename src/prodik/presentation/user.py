from http import HTTPStatus

from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter

from prodik.application.manage_credentials import (
    UpdateCurrentUserPasswordInteractor,
    UpdateCurrentUserPasswordRequestDTO,
)
from prodik.application.manage_profile import (
    UpdateCurrentUserProfileInteractor,
    UpdateCurrentUserProfileRequestDTO,
)
from prodik.presentation.schemas.user import (
    UpdateCurrentUserPasswordRequest,
    UpdateCurrentUserProfileRequest,
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


@router.put("/me/password", status_code=HTTPStatus.NO_CONTENT)
async def update_current_user_password(
    request: UpdateCurrentUserPasswordRequest,
    interactor: FromDishka[UpdateCurrentUserPasswordInteractor],
) -> None:
    await interactor.execute(
        UpdateCurrentUserPasswordRequestDTO(
            old_password=request.old_password, new_password=request.new_password
        )
    )
