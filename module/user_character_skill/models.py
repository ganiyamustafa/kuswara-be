from sqlalchemy import Column, UUID, ForeignKey, String, Integer
from sqlalchemy.orm import relationship
from core.base.models import BaseModel
import uuid

class UserCharacterSkill(BaseModel):
  id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
  name = Column(String, nullable=False)
  description = Column(String, nullable=False)
  image = Column(String, nullable=False, default="0 0 0")
  cooldown = Column(Integer, nullable=False)
  skill_type = Column(Integer, nullable=False)
  user_character_id = Column(UUID(as_uuid=True), ForeignKey('user_characters.id', ondelete="CASCADE"), nullable=False)

  user_character = relationship('UserCharacter', uselist=False, back_populates='skills')

  __tablename__ = 'user_character_skills'

  def __init__(self, hospital_facility_id, hospital_id):
      self.hospital_facility_id = hospital_facility_id
      self.hospital_id = hospital_id

  def __repr__(self):
      return '<UserCharacterSkills %r>' % self.id