from datetime import datetime, timezone
from sqlalchemy import Boolean, Column, Date, DateTime, Float, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship
from ..database import Base
from ..services.body_metrics import calc_age


class User(Base):
    """Sog'lom Pedagog foydalanuvchisi (OTM pedagog xodimi).

    Foydalanuvchi telefon raqami bilan ro'yxatdan o'tadi (yagona login
    identifikatori). Ilova sozlamalari (`font_scale`, ...)
    ham shu jadvalda — ular 1:1 va kam o'zgaradi, alohida jadval shart emas.
    """

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    phone = Column(String, unique=True, index=True, nullable=False)     # +998XXXXXXXXX — yagona login identifikatori

    full_name = Column(String, nullable=False)
    gender = Column(String, nullable=True)

    # ── tana ko'rsatkichlari ──────────────────────────────────────────────────
    birth_date = Column(Date, nullable=True)
    height_cm = Column(Float, nullable=True)
    weight_kg = Column(Float, nullable=True)
    bmi = Column(Float, nullable=True)   # profil yangilanganda qayta hisoblanadi (body_metrics.py)
    bfp = Column(Float, nullable=True)   # tanadagi yog' foizi

    password_hash = Column(String, nullable=False)   # bcrypt — parol hech qachon ochiq saqlanmaydi

    # ── sozlamalar ────────────────────────────────────────────────────────────
    font_scale = Column(Float, default=1.0)
    reminder_on = Column(Boolean, default=False)
    rem_hour = Column(Integer, default=9)
    rem_min = Column(Integer, default=0)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    progress = relationship("Progress", back_populates="user", cascade="all, delete-orphan")
    exercise_progress = relationship("ExerciseProgress", back_populates="user", cascade="all, delete-orphan")
    test_results = relationship("TestResult", back_populates="user", cascade="all, delete-orphan")

    @property
    def age(self) -> int | None:
        """Tug'ilgan sanadan hisoblangan yosh — bazada saqlanmaydi, doim aniq."""
        return calc_age(self.birth_date)

    @property
    def is_admin(self) -> bool:
        """Telefon raqami ADMIN_PHONES ro'yxatida bo'lsa — admin (parol tiklay oladi)."""
        from ..config import ADMIN_PHONES
        return self.phone in ADMIN_PHONES


class Progress(Base):
    """Bir haftalik-sessiyalik mashg'ulotning yakuni (RPE bilan)."""

    __tablename__ = "progress"
    __table_args__ = (UniqueConstraint("user_id", "week", "session", name="uq_progress_user_week_session"),)

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    week = Column(Integer, nullable=False)
    session = Column(Integer, nullable=False)
    rpe = Column(Integer, nullable=False)
    completed_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="progress")


class ExerciseProgress(Base):
    """Sessiya ichidagi bitta individual mashqning bajarilishi (taymer tugagan payt)."""

    __tablename__ = "exercise_progress"
    __table_args__ = (
        UniqueConstraint("user_id", "week", "session", "exercise_index", name="uq_exercise_progress_user_week_session_ex"),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    week = Column(Integer, nullable=False)
    session = Column(Integer, nullable=False)
    exercise_index = Column(Integer, nullable=False)  # majmua ichidagi tartib raqami (0-based)
    completed_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="exercise_progress")


class TestResult(Base):
    """Funksional test natijasi (masalan `smt`, `saet`, `pet`, ...)."""

    __tablename__ = "test_results"
    __table_args__ = (UniqueConstraint("user_id", "test_id", name="uq_test_results_user_test"),)

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    test_id = Column(String, nullable=False)
    value = Column(Float, nullable=False)
    recorded_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="test_results")
