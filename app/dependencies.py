import secrets
from typing import Annotated, Any, Literal

from fastapi import Depends, HTTPException, Request
from fastapi.templating import Jinja2Templates
from sqlmodel.ext.asyncio.session import AsyncSession
from starlette.responses import Response

from app.database import get_session

SessionDep = Annotated[AsyncSession, Depends(get_session)]

templates = Jinja2Templates(directory="templates")


def add_flash(
    request: Request,
    text: str,
    category: Literal["success", "warning", "info"] = "info",
) -> None:
    messages = list(request.session.get("flash_messages", []))
    messages.append({"category": category, "text": text})
    request.session["flash_messages"] = messages


def get_csrf_token(request: Request) -> str:
    token = request.session.get("csrf_token")
    if token is None:
        token = secrets.token_urlsafe(32)
        request.session["csrf_token"] = token
    return str(token)


def verify_csrf_token(request: Request, submitted_token: str) -> None:
    expected_token = request.session.get("csrf_token")
    if expected_token is None or not secrets.compare_digest(
        str(expected_token),
        submitted_token,
    ):
        raise HTTPException(status_code=403, detail="Invalid CSRF token")


# Единая точка отрисовки: flash-сообщения удаляются из сессии при чтении,
# поэтому забыть их в одном обработчике значит показать сообщение на чужой
# странице. Токен формы подставляется здесь же.
def render(
    request: Request,
    name: str,
    context: dict[str, Any] | None = None,
    status_code: int = 200,
) -> Response:
    return templates.TemplateResponse(
        request=request,
        name=name,
        context={
            **(context or {}),
            "flash_messages": request.session.pop("flash_messages", []),
            "csrf_token": get_csrf_token(request),
        },
        status_code=status_code,
    )
