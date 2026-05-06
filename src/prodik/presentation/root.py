from http import HTTPStatus

import structlog
from fastapi import APIRouter

router = APIRouter()

logger = structlog.get_logger()


@router.get("/")
async def root() -> dict[str, int]:
    return {"status": HTTPStatus.OK}
