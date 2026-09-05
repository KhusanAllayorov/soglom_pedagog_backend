"""Sxema migratsiyalari.

`Base.metadata.create_all()` mavjud jadvalga yangi ustun qo'shmaydi, shuning
uchun keyin qo'shilgan ustunlar shu yerda qo'lda ALTER qilinadi. Barcha
amallar **idempotent** — bir necha marta ishga tushsa ham zarari yo'q.
SQLite va PostgreSQL ikkalasida ishlaydi.
"""

from sqlalchemy import inspect, text
from sqlalchemy.engine import Engine

from .config import ADMIN_PHONES


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

        # Login endi faqat telefon orqali — email/username butunlay olib tashlandi.
        if "email" in user_cols:
            conn.exec_driver_sql("ALTER TABLE users DROP COLUMN email")
        if "username" in user_cols:
            conn.exec_driver_sql("ALTER TABLE users DROP COLUMN username")

        for col, coltype in (
            ("birth_date", "DATE"),
            ("height_cm", "FLOAT"),
            ("weight_kg", "FLOAT"),
            ("bmi", "FLOAT"),
            ("bfp", "FLOAT"),
        ):
            if col not in user_cols:
                conn.exec_driver_sql(f"ALTER TABLE users ADD COLUMN {col} {coltype}")

        # Rollar: admin / instructor / pedagog_hodim. Yangi ustun — mavjud
        # foydalanuvchilar 'pedagog_hodim' bilan boshlanadi.
        if "role" not in user_cols:
            conn.exec_driver_sql(
                "ALTER TABLE users ADD COLUMN role VARCHAR NOT NULL DEFAULT 'pedagog_hodim'"
            )

        # ADMIN_PHONES ro'yxatidagi raqamlarni admin qilib qo'yamiz (bootstrap).
        # Faqat ko'tarish — bu yerda hech kimni admin lavozimidan tushirmaymiz.
        for phone in ADMIN_PHONES:
            conn.execute(text("UPDATE users SET role = 'admin' WHERE phone = :phone"), {"phone": phone})
