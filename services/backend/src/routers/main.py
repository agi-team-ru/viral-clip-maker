import logging
from fastapi import APIRouter, Request


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/main")


@router.get("")
async def read(request: Request):
    return ["Hello"]
