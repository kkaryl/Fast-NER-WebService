from fastapi import APIRouter
from fastapi_versioning import version

router = APIRouter()


@router.get("/ping")
@version(1, 0)
async def pong():
    return {"ping": "pong!"}