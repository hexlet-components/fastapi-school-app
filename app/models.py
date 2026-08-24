from sqlmodel import Field, SQLModel


class Course(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str
    description: str = ""


class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    email: str
    # Пароль хранится в открытом виде: приложение показывает работу с формами
    # и базой, аутентификации в нём нет.
    password: str
