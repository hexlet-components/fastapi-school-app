from fastapi import APIRouter, Form, HTTPException, Request
from pydantic import ValidationError
from sqlmodel import select
from starlette.responses import RedirectResponse, Response

from app.dependencies import SessionDep, add_flash, render, verify_csrf_token
from app.forms import UserForm, error_messages
from app.models import User

router = APIRouter(prefix="/users")


async def find_user(session: SessionDep, user_id: int) -> User:
    user = await session.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("", name="users")
async def index(request: Request, session: SessionDep) -> Response:
    users = (await session.exec(select(User).order_by(User.id))).all()
    return render(request, "users/index.html", {"users": users})


# Литеральный сегмент объявляется до параметра, иначе «/users/{user_id}»
# принял бы запрос «/users/new».
@router.get("/new", name="new_user")
async def new(request: Request) -> Response:
    return render(request, "users/new.html", {"form": {}, "errors": []})


@router.get("/{user_id}", name="user")
async def show(
    request: Request,
    session: SessionDep,
    user_id: int,
) -> Response:
    user = await find_user(session, user_id)
    return render(request, "users/show.html", {"user": user})


@router.get("/{user_id}/edit", name="edit_user")
async def edit(
    request: Request,
    session: SessionDep,
    user_id: int,
) -> Response:
    user = await find_user(session, user_id)
    return render(
        request,
        "users/edit.html",
        {"user": user, "form": user, "errors": []},
    )


@router.post("", name="create_user")
async def create(
    request: Request,
    session: SessionDep,
    csrf_token: str = Form(""),
    name: str = Form(""),
    email: str = Form(""),
    password: str = Form(""),
    password_confirmation: str = Form(""),
) -> Response:
    verify_csrf_token(request, csrf_token)
    form = {"name": name, "email": email}

    try:
        data = UserForm.model_validate(
            {
                **form,
                "password": password,
                "password_confirmation": password_confirmation,
            }
        )
    except ValidationError as error:
        return render(
            request,
            "users/new.html",
            {"form": form, "errors": error_messages(error)},
            status_code=422,
        )

    session.add(User(name=data.name, email=data.email, password=data.password))
    await session.commit()

    add_flash(request, "Пользователь успешно создан", "success")
    return RedirectResponse(request.url_for("users"), status_code=303)


@router.post("/{user_id}/edit", name="update_user")
async def update(
    request: Request,
    session: SessionDep,
    user_id: int,
    csrf_token: str = Form(""),
    name: str = Form(""),
    email: str = Form(""),
    password: str = Form(""),
    password_confirmation: str = Form(""),
) -> Response:
    verify_csrf_token(request, csrf_token)
    user = await find_user(session, user_id)
    form = {"name": name, "email": email}

    try:
        data = UserForm.model_validate(
            {
                **form,
                "password": password,
                "password_confirmation": password_confirmation,
            }
        )
    except ValidationError as error:
        return render(
            request,
            "users/edit.html",
            {"user": user, "form": form, "errors": error_messages(error)},
            status_code=422,
        )

    user.name = data.name
    user.email = data.email
    user.password = data.password
    session.add(user)
    await session.commit()

    add_flash(request, "Пользователь успешно отредактирован", "success")
    return RedirectResponse(request.url_for("users"), status_code=303)


@router.post("/{user_id}/delete", name="delete_user")
async def delete(
    request: Request,
    session: SessionDep,
    user_id: int,
    csrf_token: str = Form(""),
) -> Response:
    verify_csrf_token(request, csrf_token)
    user = await find_user(session, user_id)
    await session.delete(user)
    await session.commit()

    add_flash(request, "Пользователь успешно удалён", "success")
    return RedirectResponse(request.url_for("users"), status_code=303)
