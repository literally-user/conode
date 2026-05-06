from http import HTTPStatus

from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def root() -> dict[str, int]:
    return {"status": HTTPStatus.OK}