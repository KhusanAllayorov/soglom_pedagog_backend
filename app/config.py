from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./soglom_pedagog.db")

# Railway PostgreSQL plagini ba'zan "postgres://" prefiksini beradi,
# SQLAlchemy 2.0 esa "postgresql://" talab qiladi — moslashtiramiz.
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "43200"))

# Admin amallar (parol tiklash) uchun maxfiy kalit. Bo'sh bo'lsa — admin API o'chiq.
ADMIN_KEY = os.getenv("ADMIN_KEY", "")
