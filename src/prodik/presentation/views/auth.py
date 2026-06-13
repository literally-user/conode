from http import HTTPStatus

from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter

from prodik.application.authorization import (
    LoginInteractor,
    LoginRequestDTO,
    RefreshTokenInteractor,
    RegisterInteractor,
    RegisterRequestDTO,
)
from prodik.presentation.schemas.auth import (
    AuthResponse,
    LoginRequest,
    RefreshTokenRequest,
    RegisterRequest,
)

router = APIRouter(tags=["authorization"], route_class=DishkaRoute, prefix="/auth")


@router.post("/register", status_code=HTTPStatus.CREATED)
async def register(
    request: RegisterRequest,
    interactor: FromDishka[RegisterInteractor],
) -> AuthResponse:
    result = await interactor.execute(
        RegisterRequestDTO(
            first_name=request.first_name,
            last_name=request.last_name,
            username=request.username,
            password=request.password,
            email=request.email,
        ),
    )

    return AuthResponse(
        access_token=result.access_token,
        refresh_token=result.refresh_token,
        expires_in=result.expires_in,
    )


@router.post("/login")
async def login(
    request: LoginRequest,
    interactor: FromDishka[LoginInteractor],
) -> AuthResponse:
    result = await interactor.execute(
        LoginRequestDTO(
            password=request.password,
            email=request.email,
        ),
    )

    return AuthResponse(
        access_token=result.access_token,
        refresh_token=result.refresh_token,
        expires_in=result.expires_in,
    )


@router.post("/refresh")
async def refresh_token(
    request: RefreshTokenRequest,
    interactor: FromDishka[RefreshTokenInteractor],
) -> AuthResponse:
    result = await interactor.execute(request.refresh_token)

    return AuthResponse(
        access_token=result.access_token,
        refresh_token=result.refresh_token,
        expires_in=result.expires_in,
    )
