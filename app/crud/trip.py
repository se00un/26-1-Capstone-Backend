from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.models.trip import Trip, TripMember, Invitation
from app.schemas.trip import TripCreate
import uuid
from datetime import datetime, timedelta

def get_trip_by_id(db: Session, trip_id: int):
    return db.query(Trip).filter(Trip.id == trip_id).first()

def get_trip_member(db: Session, trip_id: int, user_id: int):
    return db.query(TripMember).filter(TripMember.trip_id == trip_id, TripMember.user_id == user_id).first()

def create_trip(db: Session, trip_in: TripCreate, owner_id: int):
    db_trip = Trip(
        owner_id=owner_id,
        title=trip_in.title,
        start_date=trip_in.start_date,
        end_date=trip_in.end_date,
        is_group_trip=trip_in.is_group_trip,
        status="ongoing"
    )
    db.add(db_trip)
    db.commit()
    db.refresh(db_trip)

    db_member = TripMember(
        trip_id=db_trip.id,
        user_id=owner_id,
        role="owner"
    )
    db.add(db_member)
    db.commit()
    return db_trip

def get_my_trips(db: Session, user_id: int):
    return db.query(Trip).join(TripMember).filter(TripMember.user_id == user_id).all()

def create_invitation(db: Session, trip_id: int, inviter_id: int, expires_at: datetime = None):
    invite_code = str(uuid.uuid4()).split('-')[0].upper()
    if not expires_at:
        expires_at = datetime.utcnow() + timedelta(days=7)
        
    db_invite = Invitation(
        trip_id=trip_id,
        invite_code=invite_code,
        invited_by=inviter_id,
        status="pending",
        expires_at=expires_at
    )
    db.add(db_invite)
    db.commit()
    db.refresh(db_invite)
    return db_invite

def get_invitation_by_code(db: Session, invite_code: str):
    return db.query(Invitation).filter(Invitation.invite_code == invite_code).first()

def add_trip_member(db: Session, trip_id: int, user_id: int, role: str = "editor"):
    existing = db.query(TripMember).filter(
        TripMember.trip_id == trip_id, 
        TripMember.user_id == user_id
    ).first()
    
    if existing:
        return existing
        
    db_member = TripMember(
        trip_id=trip_id,
        user_id=user_id,
        role=role
    )
    db.add(db_member)
    db.commit()
    db.refresh(db_member)
    return db_member

def delete_trip(db: Session, trip_id: int):
    trip = db.query(Trip).filter(Trip.id == trip_id).first()
    if trip:
        db.delete(trip)
        db.commit()
    return trip
