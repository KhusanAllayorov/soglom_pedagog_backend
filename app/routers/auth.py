from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from ..config import ADMIN_KEY
from ..database import get_db
from ..identifiers import normalize_email, normalize_phone, normalize_username
from ..models.models import User
from ..schemas.schemas import (
    AdminPasswordReset,
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    UserOut,
    UserSettingsUpdate,
)
from ..auth.jwt import create_token, hash_password, verify_password, get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])


def _clean_identifiers(body: RegisterRequest) -> dict[str, str | None]:
    """Kiritilgan identifikatorlarni tekshiradi va bir ko'rinishga keltiradi.

    Kiritilgan, lekin formati noto'g'ri bo'lsa — aniq xato qaytaradi.
    Hech biri kiritilmagan bo'lsa ham xato.
    """
    result: dict[str, str | None] = {"email": None, "phone": None, "username": None}

    if body.email and body.email.strip():
        result["email"] = normalize_email(body.email)
        if result["email"] is None:
            raise HTTPException(status_code=400, detail="Email formati noto'g'ri")

    if body.phone and body.phone.strip():
        result["phone"] = normalize_phone(body.phone)
        if result["phone"] is None:
            raise HTTPException(
                status_code=400,
                detail="Telefon raqam noto'g'ri. Namuna: +998 90 123 45 67",
            )

    if body.username and body.username.strip():
        result["username"] = normalize_username(body.username)
        if result["username"] is None:
            raise HTTPException(
                status_code=400,
                detail="Login nomi 3–30 ta belgidan iborat bo'lsin "
                       "(kichik harf, raqam, pastki chiziq)",
            )

    if not any(result.values()):
        raise HTTPException(
            status_code=400,
            detail="Email, telefon yoki login nomidan kamida bittasini kiriting",
        )
    return result


def _ensure_unique(db: Session, identifiers: dict[str, str | None]) -> None:
    """Identifikator boshqa foydalanuvchida band emasligini tekshiradi."""
    labels = {"email": "Email", "phone": "Telefon raqam", "username": "Login nomi"}
    for field, value in identifiers.items():
        if value is None:
            continue
        if db.query(User).filter(getattr(User, field) == value).first():
            raise HTTPException(
                status_code=400,
                detail=f"{labels[field]} allaqachon ro'yxatdan o'tgan",
            )


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(body: RegisterRequest, db: Session = Depends(get_db)):
    identifiers = _clean_identifiers(body)
    _ensure_unique(db, identifiers)

    user = User(
        **identifiers,
        full_name=body.full_name.strip(),
        gender=body.gender,
        age=body.age,
        password_hash=hash_password(body.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return TokenResponse(token=create_token(user.id))


def _find_by_identifier(db: Session, raw: str) -> User | None:
    """Email, telefon yoki login nomi bo'yicha foydalanuvchini topadi.

    Kiritilgan matn qaysi turga o'xshasa, o'sha ustunlar bo'yicha qidiriladi —
    shuning uchun foydalanuvchi turini oldindan tanlashi shart emas.
    """
    if not raw:
        return None

    filters = []
    if (email := normalize_email(raw)) is not None:
        filters.append(User.email == email)
    if (phone := normalize_phone(raw)) is not None:
        filters.append(User.phone == phone)
    if (username := normalize_username(raw)) is not None:
        filters.append(User.username == username)

    if not filters:
        return None
    return db.query(User).filter(or_(*filters)).first()


@router.post("/login", response_model=TokenResponse)
def login(body: LoginRequest, db: Session = Depends(get_db)):
    user = _find_by_identifier(db, body.identifier)
    if not user or not verify_password(body.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Login yoki parol noto'g'ri")
    return TokenResponse(token=create_token(user.id))


@router.get("/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_user)):
    return current_user


@router.patch("/me", response_model=UserOut)
def update_me(
    body: UserSettingsUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(current_user, field, value)
    db.commit()
    db.refresh(current_user)
    return current_user


@router.post("/admin/reset-password")
def admin_reset_password(
    body: AdminPasswordReset,
    db: Session = Depends(get_db),
    x_admin_key: str | None = Header(default=None),
):
    """Foydalanuvchi parolini unutsa, admin yangi parol o'rnatib beradi.

    Parollar bcrypt hash ko'rinishida saqlanadi — ularni «ko'rish» texnik
    jihatdan mumkin emas, tiklashning yagona to'g'ri yo'li shu.
    `X-Admin-Key` sarlavhasi `ADMIN_KEY` muhit o'zgaruvchisiga teng bo'lishi shart.
    """
    if not ADMIN_KEY or x_admin_key != ADMIN_KEY:
        raise HTTPException(status_code=403, detail="Ruxsat yo'q")
    if len(body.new_password) < 6:
        raise HTTPException(status_code=400, detail="Parol kamida 6 ta belgi bo'lsin")
    user = _find_by_identifier(db, body.identifier)
    if user is None:
        raise HTTPException(status_code=404, detail="Foydalanuvchi topilmadi")
    user.password_hash = hash_password(body.new_password)
    db.commit()
    return {"ok": True, "user_id": user.id}


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
def delete_my_account(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Hisobni butunlay o'chiradi (Google Play "account deletion" talabi).

    Foydalanuvchining progress va test natijalari `User` bilan birga
    avtomatik o'chadi (`models.py` dagi `cascade="all, delete-orphan"`).
    """
    db.delete(current_user)
    db.commit()
