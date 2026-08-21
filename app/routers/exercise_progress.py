from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.models import ExerciseProgress, User
from ..schemas.schemas import ExerciseProgressIn, ExerciseProgressOut
from ..auth.jwt import get_current_user

router = APIRouter(prefix="/exercise-progress", tags=["exercise-progress"])


@router.get("", response_model=list[ExerciseProgressOut])
def list_exercise_progress(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return (
        db.query(ExerciseProgress)
        .filter(ExerciseProgress.user_id == current_user.id)
        .order_by(ExerciseProgress.week, ExerciseProgress.session, ExerciseProgress.exercise_index)
        .all()
    )


@router.post("", response_model=ExerciseProgressOut, status_code=201)
def mark_exercise_done(
    body: ExerciseProgressIn,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Bitta mashqning bajarilganini belgilaydi (idempotent — allaqachon bor bo'lsa qayta yozmaydi)."""
    row = (
        db.query(ExerciseProgress)
        .filter(
            ExerciseProgress.user_id == current_user.id,
            ExerciseProgress.week == body.week,
            ExerciseProgress.session == body.session,
            ExerciseProgress.exercise_index == body.exercise_index,
        )
        .first()
    )
    if not row:
        row = ExerciseProgress(
            user_id=current_user.id, week=body.week, session=body.session, exercise_index=body.exercise_index
        )
        db.add(row)
        db.commit()
        db.refresh(row)
    return row
