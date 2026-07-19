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
    is_admin: bool = False
    telegram_chat_id: str | None = None

    model_config = {"from_attributes": True}


# --- admin: kelola user ---
class AdminUserOut(BaseModel):
    id: int
    username: str
    is_admin: bool
    telegram_linked: bool
    tx_count: int


class UserCreate(BaseModel):
    username: str = Field(min_length=1, max_length=50)
    password: str = Field(min_length=8)
    is_admin: bool = False


class AdminUserUpdate(BaseModel):
    password: str | None = Field(default=None, min_length=8)
    is_admin: bool | None = None
    unlink_telegram: bool = False


# --- self-service tautan Telegram ---
class LinkCodeOut(BaseModel):
    code: str
    expires_at: str
