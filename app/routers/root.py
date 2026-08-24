from fastapi import APIRouter, Request
from starlette.responses import Response

from app.dependencies import render

router = APIRouter()


@router.get("/", name="home")
async def home(request: Request) -> Response:
    return render(request, "index.html")
