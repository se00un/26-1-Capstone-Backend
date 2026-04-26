from sqlalchemy import Column, String, DateTime, BigInteger, ForeignKey, func, Integer, DECIMAL, Text
from sqlalchemy.orm import relationship
from app.db.database import Base

class Route(Base):
    __tablename__ = "routes"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    trip_id = Column(BigInteger, ForeignKey("trips.id"))
    title = Column(String(255))
    created_by = Column(BigInteger, ForeignKey("users.id"))

    # Relationships
    trip = relationship("Trip", back_populates="routes")
    creator = relationship("User", back_populates="created_routes")
    places = relationship("RoutePlace", back_populates="route")

class RoutePlace(Base):
    __tablename__ = "route_places"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    route_id = Column(BigInteger, ForeignKey("routes.id"))
    place_name = Column(String(255), nullable=False)
    latitude = Column(DECIMAL(10, 6), nullable=False)
    longitude = Column(DECIMAL(10, 6), nullable=False)
    visit_order = Column(Integer, nullable=False)
    memo = Column(Text)
    visited_at = Column(DateTime(timezone=True))

    # Relationships
    route = relationship("Route", back_populates="places")
