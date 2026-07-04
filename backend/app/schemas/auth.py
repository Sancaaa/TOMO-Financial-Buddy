from pydantic import BaseModel


class LoginRequest(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    id: int
    username: str
    telegram_chat_id: str | None = None

    model_config = {"from_attributes": True}
