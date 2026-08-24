from fastapi import APIRouter, Form, HTTPException, Request
from pydantic import ValidationError
from sqlmodel import select
from starlette.responses import RedirectResponse, Response

from app.dependencies import SessionDep, add_flash, render, verify_csrf_token
from app.forms import CourseForm, error_messages
from app.models import Course

router = APIRouter(prefix="/courses")


async def find_course(session: SessionDep, course_id: int) -> Course:
    course = await session.get(Course, course_id)
    if course is None:
        raise HTTPException(status_code=404, detail="Course not found")
    return course


@router.get("", name="courses")
async def index(
    request: Request,
    session: SessionDep,
    title: str = "",
) -> Response:
    statement = select(Course).order_by(Course.id)
    if title:
        statement = statement.where(Course.title.like(f"%{title}%"))
    courses = (await session.exec(statement)).all()
    return render(request, "courses/index.html", {"courses": courses})


# Маршруты с литеральным сегментом объявляются до маршрутов с параметром:
# FastAPI выбирает первое совпадение по порядку объявления, поэтому
# «/courses/{course_id}» иначе принял бы запрос «/courses/new».
@router.get("/new", name="new_course")
async def new(request: Request) -> Response:
    return render(request, "courses/new.html", {"form": {}, "errors": []})


@router.get("/{course_id}", name="course")
async def show(
    request: Request,
    session: SessionDep,
    course_id: int,
) -> Response:
    course = await find_course(session, course_id)
    return render(request, "courses/show.html", {"course": course})


@router.get("/{course_id}/edit", name="edit_course")
async def edit(
    request: Request,
    session: SessionDep,
    course_id: int,
) -> Response:
    course = await find_course(session, course_id)
    return render(
        request,
        "courses/edit.html",
        {"course": course, "form": course, "errors": []},
    )


@router.post("", name="create_course")
async def create(
    request: Request,
    session: SessionDep,
    csrf_token: str = Form(""),
    title: str = Form(""),
    description: str = Form(""),
) -> Response:
    verify_csrf_token(request, csrf_token)
    form = {"title": title, "description": description}

    try:
        data = CourseForm.model_validate(form)
    except ValidationError as error:
        return render(
            request,
            "courses/new.html",
            {"form": form, "errors": error_messages(error)},
            status_code=422,
        )

    session.add(Course(**data.model_dump()))
    await session.commit()

    add_flash(request, "Курс успешно создан", "success")
    return RedirectResponse(request.url_for("courses"), status_code=303)


@router.post("/{course_id}/edit", name="update_course")
async def update(
    request: Request,
    session: SessionDep,
    course_id: int,
    csrf_token: str = Form(""),
    title: str = Form(""),
    description: str = Form(""),
) -> Response:
    verify_csrf_token(request, csrf_token)
    course = await find_course(session, course_id)
    form = {"title": title, "description": description}

    try:
        data = CourseForm.model_validate(form)
    except ValidationError as error:
        return render(
            request,
            "courses/edit.html",
            {"course": course, "form": form, "errors": error_messages(error)},
            status_code=422,
        )

    course.title = data.title
    course.description = data.description
    session.add(course)
    await session.commit()

    add_flash(request, "Курс успешно отредактирован", "success")
    return RedirectResponse(request.url_for("courses"), status_code=303)


@router.post("/{course_id}/delete", name="delete_course")
async def delete(
    request: Request,
    session: SessionDep,
    course_id: int,
    csrf_token: str = Form(""),
) -> Response:
    verify_csrf_token(request, csrf_token)
    course = await find_course(session, course_id)
    await session.delete(course)
    await session.commit()

    add_flash(request, "Курс успешно удалён", "success")
    return RedirectResponse(request.url_for("courses"), status_code=303)
