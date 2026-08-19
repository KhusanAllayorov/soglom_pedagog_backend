"""Sxema migratsiyalari.

`Base.metadata.create_all()` mavjud jadvalga yangi ustun qo'shmaydi, shuning
uchun keyin qo'shilgan ustunlar shu yerda qo'lda ALTER qilinadi. Barcha
amallar **idempotent** — bir necha marta ishga tushsa ham zarari yo'q.
SQLite va PostgreSQL ikkalasida ishlaydi.
"""

from sqlalchemy import inspect
from sqlalchemy.engine import Engine


def run_migrations(engine: Engine) -> None:
    insp = inspect(engine)
    user_cols = {c["name"] for c in insp.get_columns("users")}

    with engine.begin() as conn:
        # password_plain olib tashlangan (xavfsizlik: parol faqat bcrypt hash
        # ko'rinishida saqlanadi) — eski bazalarda ustunni o'chiramiz.
        if "password_plain" in user_cols:
            conn.exec_driver_sql("ALTER TABLE users DROP COLUMN password_plain")

        # 'age' (matn) o'rniga 'birth_date' + hisoblangan BMI/BFP.
        if "age" in user_cols:
            conn.exec_driver_sql("ALTER TABLE users DROP COLUMN age")

        # Ovozli yo'riqnoma (TTS) funksiyasi olib tashlandi — 'voice' sozlamasi kerak emas.
        if "voice" in user_cols:
            conn.exec_driver_sql("ALTER TABLE users DROP COLUMN voice")

        for col, coltype in (
            ("birth_date", "DATE"),
            ("height_cm", "FLOAT"),
            ("weight_kg", "FLOAT"),
            ("bmi", "FLOAT"),
            ("bfp", "FLOAT"),
        ):
            if col not in user_cols:
                conn.exec_driver_sql(f"ALTER TABLE users ADD COLUMN {col} {coltype}")
