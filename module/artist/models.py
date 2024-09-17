from sqlalchemy import Column, String, DateTime, func, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from core.base.models import BaseModel
import uuid

class Artist(BaseModel):
  id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
  name = Column(String, nullable=False)

  songs = relationship('Song', secondary='song_artists', back_populates='artists')

  __tablename__ = 'artists'

  class Config:
    orm_mode = True
    from_attributes = True

  def __init__(self, name):
    self.name = name

  def __repr__(self):
    return '<Artists %r>' % self.name
