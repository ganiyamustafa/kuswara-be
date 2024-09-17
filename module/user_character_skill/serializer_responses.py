from uuid import UUID
from core.base.serializer_response import OrmBaseSerializerModel

class UserCharacterSkillResponse(OrmBaseSerializerModel):
  id: UUID
  name: str
  description: str
  cooldown: int
  skill_type: int

  @classmethod
  def from_each_orm(cls, skills):
    return [cls.from_orm(skill) for skill in skills]