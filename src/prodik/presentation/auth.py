from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter

from prodik.application.authorization import RegisterInteractor, RegisterRequestDTO
from prodik.presentation.schemas.auth import AuthResponse, RegisterRequest

router = APIRouter(tags=["authorization"], route_class=DishkaRoute, prefix="/auth")


@router.post("/register")
async def register(
    request: RegisterRequest, interactor: FromDishka[RegisterInteractor]
) -> AuthResponse:
    result = await interactor.execute(
        RegisterRequestDTO(
            first_name=request.first_name,
            last_name=request.last_name,
            username=request.username,
            password=request.password,
            email=request.email,
        )
    )

    return AuthResponse(
        access_token=result.access_token,
        refresh_token=result.refresh_token,
        expires_in=result.expires_in,
    )
