# SQLAlchemy models will be defined here 
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship, declarative_base
import datetime

Base = declarative_base()

class Event(Base):
    __tablename__ = 'events'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    location = Column(String, nullable=False)
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=False)
    max_capacity = Column(Integer, nullable=False)
    attendees = relationship('Registration', back_populates='event', cascade="all, delete-orphan")

class Attendee(Base):
    __tablename__ = 'attendees'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True, index=True)
    registrations = relationship('Registration', back_populates='attendee', cascade="all, delete-orphan")

class Registration(Base):
    __tablename__ = 'registrations'
    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey('events.id', ondelete='CASCADE'))
    attendee_id = Column(Integer, ForeignKey('attendees.id', ondelete='CASCADE'))
    __table_args__ = (UniqueConstraint('event_id', 'attendee_id', name='_event_attendee_uc'),)
    event = relationship('Event', back_populates='attendees')
    attendee = relationship('Attendee', back_populates='registrations') 