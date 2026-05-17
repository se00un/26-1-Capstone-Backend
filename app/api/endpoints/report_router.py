from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.api.deps import get_current_user
from app.models import TripReport, TripMember
from app.services.report_service import generate_trip_report
from app.schemas.trip_reports import TripReportResponse

router = APIRouter()


@router.post("/{trip_id}/generate", response_model=TripReportResponse, status_code=201)
def generate_report(
    trip_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    member = (
        db.query(TripMember)
        .filter(
            TripMember.trip_id == trip_id,
            TripMember.user_id == current_user.id,
        )
        .first()
    )
    if not member:
        raise HTTPException(status_code=403, detail="Not a member of this trip.")

    return generate_trip_report(
        trip_id=trip_id,
        current_user_id=current_user.id,
        db=db,
    )


@router.get("/{trip_id}", response_model=TripReportResponse)
def get_report(
    trip_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    member = (
        db.query(TripMember)
        .filter(
            TripMember.trip_id == trip_id,
            TripMember.user_id == current_user.id,
        )
        .first()
    )
    if not member:
        raise HTTPException(status_code=403, detail="Not a member of this trip.")

    report = (
        db.query(TripReport)
        .filter(TripReport.trip_id == trip_id)
        .first()
    )
    if not report:
        raise HTTPException(status_code=404, detail="Report not found.")

    return report