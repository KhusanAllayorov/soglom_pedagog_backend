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

    # password_plain olib tashlangan (xavfsizlik: parol faqat bcrypt hash
    # ko'rinishida saqlanadi) — eski bazalarda ustunni o'chiramiz.
    user_cols = {c["name"] for c in insp.get_columns("users")}
    if "password_plain" in user_cols:
        with engine.begin() as conn:
            conn.exec_driver_sql("ALTER TABLE users DROP COLUMN password_plain")
