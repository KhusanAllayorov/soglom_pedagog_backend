from datetime import date, datetime
from pydantic import BaseModel


# ── Auth ──────────────────────────────────────────────────────────────────────

class RegisterRequest(BaseModel):
    """Ro'yxatdan o'tish — telefon raqami va parol majburiy.

    `birth_date`, `height_cm`, `weight_kg` — ixtiyoriy (BMI/BFP shular bilan hisoblanadi).
    """

    full_name: str
    phone: str                    # +998 XX XXX XX XX — yagona login identifikatori
    password: str
    gender: str | None = None
    birth_date: date | None = None
    height_cm: float | None = None
    weight_kg: float | None = None


class LoginRequest(BaseModel):
    """Kirish — `identifier` telefon raqami."""

    password: str
    identifier: str


class TokenResponse(BaseModel):
    token: str
    token_type: str = "bearer"


class AdminPasswordReset(BaseModel):
    """Admin foydalanuvchiga yangi parol o'rnatadi (`identifier` — telefon raqami)."""

    identifier: str
    new_password: str


class UserOut(BaseModel):
    id: int
    phone: str
    full_name: str
    role: str = "pedagog_hodim"
    is_admin: bool = False
    is_staff: bool = False
    gender: str | None = None
    birth_date: date | None = None
    age: int | None = None          # birth_date'dan hisoblanadi, bazada saqlanmaydi
    height_cm: float | None = None
    weight_kg: float | None = None
    bmi: float | None = None
    bfp: float | None = None
    font_scale: float
    reminder_on: bool
    rem_hour: int
    rem_min: int

    model_config = {"from_attributes": True}


class UserSettingsUpdate(BaseModel):
    """`/auth/me` PATCH — faqat yuborilgan maydonlar yangilanadi.

    `birth_date`, `height_cm`, `weight_kg` o'zgarganda `bmi`/`bfp` avtomatik qayta hisoblanadi.
    """

    full_name: str | None = None
    gender: str | None = None
    birth_date: date | None = None
    height_cm: float | None = None
    weight_kg: float | None = None
    font_scale: float | None = None
    reminder_on: bool | None = None
    rem_hour: int | None = None
    rem_min: int | None = None


# ── Admin ─────────────────────────────────────────────────────────────────────

ROLES = ("admin", "instructor", "pedagog_hodim")


class AdminUserUpdate(BaseModel):
    """Admin foydalanuvchi profilini tahrirlashi (`PATCH /admin/users/{id}`)."""

    full_name: str | None = None
    gender: str | None = None
    birth_date: date | None = None
    height_cm: float | None = None
    weight_kg: float | None = None


class RoleUpdate(BaseModel):
    """Admin foydalanuvchi rolini o'zgartirishi (`PATCH /admin/users/{id}/role`)."""

    role: str


class OverviewUser(BaseModel):
    """Excel eksport uchun — bitta foydalanuvchining umumiy ko'rsatkichlari."""

    id: int
    full_name: str
    phone: str
    role: str
    sessions_done: int
    test_results: dict[str, float]


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


# ── Individual mashq bajarilishi ────────────────────────────────────────────────

class ExerciseProgressIn(BaseModel):
    week: int
    session: int
    exercise_index: int


class ExerciseProgressOut(BaseModel):
    week: int
    session: int
    exercise_index: int
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
