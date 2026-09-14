# fastapi-school-app

[![Python CI](https://github.com/hexlet-components/fastapi-school-app/actions/workflows/python-ci.yml/badge.svg)](https://github.com/hexlet-components/fastapi-school-app/actions/workflows/python-ci.yml)

## Зачем это нужно

Учебное приложение на [FastAPI](https://fastapi.tiangolo.com/): курсы и
пользователи школы. Сделано как самостоятельная работа курса по FastAPI, поэтому
показывает собранный проект целиком: маршруты, шаблоны Jinja2, валидацию формы,
сессию с одноразовыми сообщениями и работу с базой через SQLModel.

## Requirement

- Python 3.14

## Структура

```text
app/main.py          точка входа: приложение, сессия, подключение роутеров
app/database.py      движок SQLite, сессия запроса, создание таблиц и данных
app/models.py        таблицы SQLModel
app/forms.py         схемы Pydantic для проверки форм
app/dependencies.py  шаблоны, отрисовка страницы, flash и CSRF-токен
app/routers/         обработчики запросов, по файлу на сущность
templates/           шаблоны Jinja2
tests/               прогон страниц и форм через TestClient
```

Страницы открываются запросом `GET`, изменения отправляются формами с методом
`POST`: браузер других глаголов в формах не поддерживает, поэтому обновление и
удаление объявлены на маршрутах `/{id}/edit` и `/{id}/delete`.

Таблицы и начальные данные создаются на старте приложения, история схемы не
ведётся. Адрес базы задаёт переменная `DATABASE_URL`, по умолчанию это файл
_school.sqlite_ в корне проекта.

## Commands

```bash
make install
make dev
make test
make lint
```

---

[![Hexlet Ltd. logo](https://raw.githubusercontent.com/Hexlet/assets/master/images/hexlet_logo128.png)](https://hexlet.io?utm_source=github&utm_medium=link&utm_campaign=fastapi-school-app)

This repository is created and maintained by the team and the community of Hexlet, an educational project. [Read more about Hexlet](https://hexlet.io?utm_source=github&utm_medium=link&utm_campaign=fastapi-school-app).
