"""Yosh, BMI, BFP hisoblash — mamun_fit_ai loyihasidagi formula asosida.

BFP (Deurenberg formulasi): (1.20 * BMI) + (0.23 * yosh) - (10.8 * jins) - 5.4
Jins koeffitsienti: erkak — 1.0, ayol — 0.0.
"""

from __future__ import annotations

from datetime import date
from typing import Protocol


def calc_age(birth_date: date | None) -> int | None:
    """Tug'ilgan sanadan to'liq yil hisobida aniq yosh (tug'ilgan kun hisobga olinadi)."""
    if birth_date is None:
        return None
    today = date.today()
    age = today.year - birth_date.year
    if (today.month, today.day) < (birth_date.month, birth_date.day):
        age -= 1
    return max(0, age)


def calc_bmi(weight_kg: float | None, height_cm: float | None) -> float | None:
    """Tana massa indeksi: vazn(kg) / bo'y(m)^2."""
    if not weight_kg or not height_cm or weight_kg <= 0 or height_cm <= 0:
        return None
    h = height_cm / 100.0
    return round(weight_kg / (h * h), 1)


def calc_bfp(bmi: float | None, age: int | None, gender: str | None) -> float | None:
    """Tanadagi yog' foizi. BMI va yosh bo'lmasa hisoblanmaydi."""
    if bmi is None or age is None:
        return None
    g = 1.0 if (gender or "").strip().lower() == "erkak" else 0.0
    bfp = (1.20 * bmi) + (0.23 * age) - (10.8 * g) - 5.4
    return round(max(0.0, min(bfp, 60.0)), 1)


class _HasBodyFields(Protocol):
    birth_date: date | None
    height_cm: float | None
    weight_kg: float | None
    gender: str | None
    bmi: float | None
    bfp: float | None


def recompute_body_metrics(user: _HasBodyFields) -> None:
    """`user.bmi` / `user.bfp` ustunlarini joriy birth_date/height/weight/gender'dan qayta yozadi.

    Ro'yxatdan o'tishda va profil yangilanganda chaqiriladi — natija DB'da
    saqlanadi (foydalanuvchi so'rovi bo'yicha), shu bilan birga Flutter ilova
    ham oflayn ishlashi uchun xuddi shu formulani mustaqil qayta hisoblaydi.
    """
    age = calc_age(user.birth_date)
    user.bmi = calc_bmi(user.weight_kg, user.height_cm)
    user.bfp = calc_bfp(user.bmi, age, user.gender)
