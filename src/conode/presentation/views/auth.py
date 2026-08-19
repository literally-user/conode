from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter

from conode.application.auth import (
    LoginInteractor,
    LoginRequestDTO,
    RegisterInteractor,
    RegisterRequestDTO,
)
from conode.presentation.schemas.auth import (
    AuthorizedResponse,
    LoginRequest,
    RegisterRequest,
)

router = APIRouter(prefix="/auth", tags=["Authorization"], route_class=DishkaRoute)


@router.post("/register")
async def register(
    interactor: FromDishka[RegisterInteractor], request: RegisterRequest
) -> AuthorizedResponse:
    result = await interactor.execute(
        RegisterRequestDTO(
            username=request.username,
            password=request.password.get_secret_value(),
            first_name=request.first_name,
            last_name=request.last_name,
            email=request.email,
            bio=request.bio,
        )
    )

    return AuthorizedResponse(
        access_token=result.access_token,
        refresh_token=result.refresh_token,
        expires_in=result.expires_in,
    )


@router.post("/login")
async def login(
    interactor: FromDishka[LoginInteractor], request: LoginRequest
) -> AuthorizedResponse:
    result = await interactor.execute(
        LoginRequestDTO(
            password=request.password.get_secret_value(),
            email=request.email,
        )
    )

    return AuthorizedResponse(
        access_token=result.access_token,
        refresh_token=result.refresh_token,
        expires_in=result.expires_in,
    )
