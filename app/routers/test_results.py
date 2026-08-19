from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.models import TestResult, User
from ..schemas.schemas import TestResultIn, TestResultOut
from ..auth.jwt import get_current_user

router = APIRouter(prefix="/test-results", tags=["test-results"])


@router.get("", response_model=list[TestResultOut])
def list_test_results(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(TestResult).filter(TestResult.user_id == current_user.id).order_by(TestResult.test_id).all()


@router.post("", response_model=TestResultOut, status_code=201)
def upsert_test_result(
    body: TestResultIn,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Test natijasini saqlaydi — mavjud bo'lsa `value`ni yangilaydi (upsert)."""
    row = (
        db.query(TestResult)
        .filter(TestResult.user_id == current_user.id, TestResult.test_id == body.test_id)
        .first()
    )
    if row:
        row.value = body.value
    else:
        row = TestResult(user_id=current_user.id, test_id=body.test_id, value=body.value)
        db.add(row)
    db.commit()
    db.refresh(row)
    return row
