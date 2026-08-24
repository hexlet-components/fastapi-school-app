import re

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


def csrf_token(client, url):
    page = client.get(url)
    assert page.status_code == 200
    match = re.search(r'name="csrf_token"[^>]*value="([^"]+)"', page.text)
    assert match is not None
    return match.group(1)


# Каждый тест работает со своим курсом: база одна на прогон, и опора на данные
# соседнего теста сделала бы результат зависимым от порядка запуска.
def create_course(client, title):
    token = csrf_token(client, "/courses/new")
    created = client.post(
        "/courses",
        data={"csrf_token": token, "title": title, "description": "Описание"},
    )
    assert created.status_code == 200
    assert "Курс успешно создан" in created.text

    listing = client.get("/courses", params={"title": title})
    match = re.search(r'/courses/(\d+)">\s*' + re.escape(title), listing.text)
    assert match is not None
    return int(match.group(1))


def test_pages(client):
    course_id = create_course(client, "Страницы")

    for url in ["/", "/courses", "/users", f"/courses/{course_id}"]:
        assert client.get(url).status_code == 200

    # Литеральный сегмент не должен попасть в маршрут с параметром
    assert client.get("/courses/new").status_code == 200
    assert client.get("/users/new").status_code == 200

    assert client.get("/courses/999999").status_code == 404


def test_course_crud(client):
    course_id = create_course(client, "Python")
    token = csrf_token(client, "/courses/new")

    invalid = client.post(
        "/courses",
        data={"csrf_token": token, "title": "P", "description": ""},
    )
    assert invalid.status_code == 422

    without_token = client.post("/courses", data={"title": "Python"})
    assert without_token.status_code == 403

    renamed = client.post(
        f"/courses/{course_id}/edit",
        data={"csrf_token": token, "title": "Питон", "description": ""},
    )
    assert renamed.status_code == 200
    assert "Курс успешно отредактирован" in renamed.text
    assert "Питон" in renamed.text

    deleted = client.post(
        f"/courses/{course_id}/delete",
        data={"csrf_token": token},
    )
    assert deleted.status_code == 200
    assert "Курс успешно удалён" in deleted.text
    assert client.get(f"/courses/{course_id}").status_code == 404


def test_user_password_confirmation(client):
    token = csrf_token(client, "/users/new")

    response = client.post(
        "/users",
        data={
            "csrf_token": token,
            "name": "Вася",
            "email": "vasya@example.com",
            "password": "secret",
            "password_confirmation": "other",
        },
    )
    assert response.status_code == 422
    assert "Пароль и подтверждение не совпадают" in response.text
