from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..config import ADMIN_PHONES
from ..database import get_db
from ..identifiers import normalize_phone
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
from ..services.body_metrics import recompute_body_metrics

router = APIRouter(prefix="/auth", tags=["auth"])


def _clean_phone(raw: str) -> str:
    """Telefon raqamini tekshiradi va `+998XXXXXXXXX` ko'rinishiga keltiradi."""
    phone = normalize_phone(raw)
    if phone is None:
        raise HTTPException(
            status_code=400,
            detail="Telefon raqam noto'g'ri. Namuna: +998 90 123 45 67",
        )
    return phone


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(body: RegisterRequest, db: Session = Depends(get_db)):
    if len(body.password) < 6:
        raise HTTPException(status_code=400, detail="Parol kamida 6 ta belgi bo'lsin")

    phone = _clean_phone(body.phone)
    if db.query(User).filter(User.phone == phone).first():
        raise HTTPException(status_code=400, detail="Bu telefon raqam allaqachon ro'yxatdan o'tgan")

    user = User(
        phone=phone,
        full_name=body.full_name.strip(),
        gender=body.gender,
        birth_date=body.birth_date,
        height_cm=body.height_cm,
        weight_kg=body.weight_kg,
        password_hash=hash_password(body.password),
        role="admin" if phone in ADMIN_PHONES else "pedagog_hodim",
    )
    recompute_body_metrics(user)
    db.add(user)
    db.commit()
    db.refresh(user)
    return TokenResponse(token=create_token(user.id))


def _find_by_phone(db: Session, raw: str) -> User | None:
    """Telefon raqami bo'yicha foydalanuvchini topadi."""
    phone = normalize_phone(raw)
    if phone is None:
        return None
    return db.query(User).filter(User.phone == phone).first()


@router.post("/login", response_model=TokenResponse)
def login(body: LoginRequest, db: Session = Depends(get_db)):
    user = _find_by_phone(db, body.identifier)
    if not user or not verify_password(body.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Telefon raqam yoki parol noto'g'ri")
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
    recompute_body_metrics(current_user)
    db.commit()
    db.refresh(current_user)
    return current_user


@router.post("/admin/reset-password")
def admin_reset_password(
    body: AdminPasswordReset,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Admin (ADMIN_PHONES ro'yxatidagi telefon bilan kirgan foydalanuvchi)
    boshqa foydalanuvchining parolini tiklaydi.

    Parollar bcrypt hash ko'rinishida saqlanadi — ularni "ko'rish" texnik
    jihatdan mumkin emas, tiklashning yagona to'g'ri yo'li shu.
    """
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Ruxsat yo'q — faqat admin")
    if len(body.new_password) < 6:
        raise HTTPException(status_code=400, detail="Parol kamida 6 ta belgi bo'lsin")
    user = _find_by_phone(db, body.identifier)
    if user is None:
        raise HTTPException(status_code=404, detail="Foydalanuvchi topilmadi")
    user.password_hash = hash_password(body.new_password)
    db.commit()
    return {"ok": True, "user_id": user.id, "phone": user.phone, "full_name": user.full_name}


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
def delete_my_account(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Hisobni butunlay o'chiradi (Google Play "account deletion" talabi).

    Foydalanuvchining progress va test natijalari `User` bilan birga
    avtomatik o'chadi (`models.py` dagi `cascade="all, delete-orphan"`).
    """
    db.delete(current_user)
    db.commit()
