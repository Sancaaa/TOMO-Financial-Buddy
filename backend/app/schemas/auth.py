from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    username: str
    password: str


class PasswordChange(BaseModel):
    old_password: str
    new_password: str = Field(min_length=8)


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    id: int
    username: str
    telegram_chat_id: str | None = None

    model_config = {"from_attributes": True}
