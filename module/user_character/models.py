from sqlalchemy import Column, UUID, ForeignKey, String
from sqlalchemy.orm import relationship
from core.base.models import BaseModel
import uuid

class UserCharacter(BaseModel):
  id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
  name = Column(String, nullable=False)
  description = Column(String, nullable=True)
  code = Column(String, nullable=False, unique=True)
  background_color = Column(String, nullable=False)
  color_filter = Column(String, nullable=False, default="0 0 0")
  primary_color = Column(String, nullable=False)
  secondary_color = Column(String, nullable=False)
  text_primary_color = Column(String, nullable=False)
  text_secondary_color = Column(String, nullable=False)

  skills = relationship('UserCharacterSkill', back_populates='user_character')
  users = relationship('User', back_populates='user_character')
  

  __tablename__ = 'user_characters'

  def __init__(self, hospital_facility_id, hospital_id):
      self.hospital_facility_id = hospital_facility_id
      self.hospital_id = hospital_id

  def __repr__(self):
      return '<UserCharacter %r>' % self.id