from http import HTTPStatus

from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def ping() -> dict[str, int]:
    return {"status": HTTPStatus.OK}
