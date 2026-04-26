from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.crud import trip as crud_trip
from app.schemas.trip import TripCreate
from datetime import datetime, timezone

def create_new_trip(db: Session, trip_in: TripCreate, current_user_id: int):
    return crud_trip.create_trip(db=db, trip_in=trip_in, owner_id=current_user_id)

def get_my_trips(db: Session, current_user_id: int):
    trips = crud_trip.get_my_trips(db=db, user_id=current_user_id)
    
    result = []
    for trip in trips:
        user_role = next((m.role for m in trip.members if m.user_id == current_user_id), "editor")
        trip_dict = trip.__dict__.copy()
        trip_dict["role"] = user_role
        result.append(trip_dict)
        
    return result

def generate_invite(db: Session, trip_id: int, current_user_id: int, expires_at: datetime = None):
    trip = crud_trip.get_trip_by_id(db, trip_id)
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
        
    is_member = any(m.user_id == current_user_id for m in trip.members)
    if not is_member:
         raise HTTPException(status_code=403, detail="Not authorized to invite to this trip")
         
    return crud_trip.create_invitation(db=db, trip_id=trip_id, inviter_id=current_user_id, expires_at=expires_at)

def accept_invite_code(db: Session, invite_code: str, current_user_id: int):
    invitation = crud_trip.get_invitation_by_code(db, invite_code)
    if not invitation:
        raise HTTPException(status_code=404, detail="Invalid invitation code")
        
    if invitation.status != "pending":
        raise HTTPException(status_code=400, detail="Invitation already accepted or invalid")
        
    if invitation.expires_at:
        expires_at_naive = invitation.expires_at.replace(tzinfo=None)
        if expires_at_naive < datetime.utcnow():
            raise HTTPException(status_code=400, detail="Invitation expired")
        
    db_member = crud_trip.add_trip_member(db=db, trip_id=invitation.trip_id, user_id=current_user_id, role="editor")
    
    invitation.status = "accepted"
    db.commit()
    
    return db_member
