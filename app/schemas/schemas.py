from datetime import datetime
from pydantic import BaseModel


# ── Auth ──────────────────────────────────────────────────────────────────────

class RegisterRequest(BaseModel):
    """Ro'yxatdan o'tish. Email, telefon va login nomidan kamida bittasi kerak."""

    full_name: str
    gender: str | None = None
    age: str | None = None
    password: str

    email: str | None = None
    phone: str | None = None      # +998 XX XXX XX XX
    username: str | None = None


class LoginRequest(BaseModel):
    """Kirish. `identifier` — email, telefon yoki login nomi."""

    password: str
    identifier: str


class TokenResponse(BaseModel):
    token: str
    token_type: str = "bearer"


class AdminPasswordReset(BaseModel):
    """Admin foydalanuvchiga yangi parol o'rnatadi (`identifier` — telefon/email/login)."""

    identifier: str
    new_password: str


class UserOut(BaseModel):
    id: int
    email: str | None = None
    phone: str | None = None
    username: str | None = None
    full_name: str
    gender: str | None = None
    age: str | None = None
    voice: bool
    font_scale: float
    reminder_on: bool
    rem_hour: int
    rem_min: int

    model_config = {"from_attributes": True}


class UserSettingsUpdate(BaseModel):
    """`/auth/me` PATCH — faqat yuborilgan maydonlar yangilanadi."""

    full_name: str | None = None
    gender: str | None = None
    age: str | None = None
    voice: bool | None = None
    font_scale: float | None = None
    reminder_on: bool | None = None
    rem_hour: int | None = None
    rem_min: int | None = None


# ── Progress ──────────────────────────────────────────────────────────────────

class ProgressIn(BaseModel):
    week: int
    session: int
    rpe: int


class ProgressOut(BaseModel):
    week: int
    session: int
    rpe: int
    completed_at: datetime

    model_config = {"from_attributes": True}


# ── Test natijalari ───────────────────────────────────────────────────────────

class TestResultIn(BaseModel):
    test_id: str
    value: float


class TestResultOut(BaseModel):
    test_id: str
    value: float
    recorded_at: datetime

    model_config = {"from_attributes": True}
