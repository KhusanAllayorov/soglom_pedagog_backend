from datetime import datetime, timezone
from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship
from ..database import Base


class User(Base):
    """Sog'lom Pedagog foydalanuvchisi (OTM pedagog xodimi).

    Login identifikatorlari — har biri noyob, kamida bittasi to'ldirilgan
    bo'ladi (odatda `phone`). Ilova sozlamalari (`voice`, `font_scale`, ...)
    ham shu jadvalda — ular 1:1 va kam o'zgaradi, alohida jadval shart emas.
    """

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    email = Column(String, unique=True, index=True, nullable=True)
    phone = Column(String, unique=True, index=True, nullable=True)      # +998XXXXXXXXX
    username = Column(String, unique=True, index=True, nullable=True)

    full_name = Column(String, nullable=False)
    gender = Column(String, nullable=True)
    age = Column(String, nullable=True)

    password_hash = Column(String, nullable=False)   # bcrypt — parol hech qachon ochiq saqlanmaydi

    # ── sozlamalar ────────────────────────────────────────────────────────────
    voice = Column(Boolean, default=True)
    font_scale = Column(Float, default=1.0)
    reminder_on = Column(Boolean, default=False)
    rem_hour = Column(Integer, default=9)
    rem_min = Column(Integer, default=0)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    progress = relationship("Progress", back_populates="user", cascade="all, delete-orphan")
    test_results = relationship("TestResult", back_populates="user", cascade="all, delete-orphan")


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
