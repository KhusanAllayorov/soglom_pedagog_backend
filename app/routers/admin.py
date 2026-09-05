from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..auth.jwt import get_current_user
from ..models.models import User
from ..schemas.schemas import ROLES, AdminUserUpdate, OverviewUser, RoleUpdate, UserOut
from ..services.body_metrics import recompute_body_metrics

router = APIRouter(prefix="/admin", tags=["admin"])


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Ruxsat yo'q — faqat admin")
    return current_user


def require_staff(current_user: User = Depends(get_current_user)) -> User:
    """Admin yoki instructor — Excel eksport va umumiy ko'rinish uchun."""
    if not current_user.is_staff:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Ruxsat yo'q")
    return current_user


@router.get("/users", response_model=list[UserOut])
def list_users(admin: User = Depends(require_admin), db: Session = Depends(get_db)):
    return db.query(User).order_by(User.id).all()


@router.patch("/users/{user_id}", response_model=UserOut)
def update_user(
    user_id: int,
    body: AdminUserUpdate,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="Foydalanuvchi topilmadi")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(user, field, value)
    recompute_body_metrics(user)
    db.commit()
    db.refresh(user)
    return user


@router.patch("/users/{user_id}/role", response_model=UserOut)
def update_role(
    user_id: int,
    body: RoleUpdate,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    if body.role not in ROLES:
        raise HTTPException(status_code=400, detail=f"Rol noto'g'ri, mumkin bo'lganlar: {', '.join(ROLES)}")
    if user_id == admin.id:
        raise HTTPException(status_code=400, detail="O'z rolingizni bu yerdan o'zgartira olmaysiz")
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="Foydalanuvchi topilmadi")
    user.role = body.role
    db.commit()
    db.refresh(user)
    return user


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, admin: User = Depends(require_admin), db: Session = Depends(get_db)):
    if user_id == admin.id:
        raise HTTPException(status_code=400, detail="O'zingizni bu yerdan o'chira olmaysiz")
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="Foydalanuvchi topilmadi")
    db.delete(user)
    db.commit()


@router.get("/overview", response_model=list[OverviewUser])
def overview(staff: User = Depends(require_staff), db: Session = Depends(get_db)):
    """Excel eksport uchun — barcha foydalanuvchilarning progress va test natijalari."""
    users = db.query(User).order_by(User.id).all()
    return [
        OverviewUser(
            id=u.id,
            full_name=u.full_name,
            phone=u.phone,
            role=u.role,
            sessions_done=len(u.progress),
            test_results={tr.test_id: tr.value for tr in u.test_results},
        )
        for u in users
    ]
