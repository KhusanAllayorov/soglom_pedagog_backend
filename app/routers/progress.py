from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.models import Progress, User
from ..schemas.schemas import ProgressIn, ProgressOut
from ..auth.jwt import get_current_user

router = APIRouter(prefix="/progress", tags=["progress"])


@router.get("", response_model=list[ProgressOut])
def list_progress(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(Progress).filter(Progress.user_id == current_user.id).order_by(Progress.week, Progress.session).all()


@router.post("", response_model=ProgressOut, status_code=201)
def upsert_progress(
    body: ProgressIn,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Bitta sessiya yakunini saqlaydi — mavjud bo'lsa `rpe`ni yangilaydi (upsert)."""
    row = (
        db.query(Progress)
        .filter(Progress.user_id == current_user.id, Progress.week == body.week, Progress.session == body.session)
        .first()
    )
    if row:
        row.rpe = body.rpe
    else:
        row = Progress(user_id=current_user.id, week=body.week, session=body.session, rpe=body.rpe)
        db.add(row)
    db.commit()
    db.refresh(row)
    return row
