from pydantic import (
    BaseModel,
    EmailStr,
    Field,
    ValidationError,
    model_validator,
)

# Формы описаны отдельно от таблиц, потому что модель с table=True при
# создании объекта значения не проверяет.


class CourseForm(BaseModel):
    title: str = Field(min_length=2)
    description: str = ""


class UserForm(BaseModel):
    name: str = Field(min_length=2)
    email: EmailStr
    password: str = Field(min_length=5)
    password_confirmation: str

    @model_validator(mode="after")
    def passwords_match(self) -> "UserForm":
        if self.password != self.password_confirmation:
            raise ValueError("Пароль и подтверждение не совпадают")
        return self


def error_messages(error: ValidationError) -> list[str]:
    return [
        str(item["msg"]).removeprefix("Value error, ")
        for item in error.errors()
    ]
