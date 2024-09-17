from uuid import UUID
from core.base.serializer_response import OrmBaseSerializerModel
from module.user_character.models import UserCharacter
from module.user_character_skill.serializer_responses import UserCharacterSkillResponse
from typing import List

class ImageDetail(OrmBaseSerializerModel):
  background_color: str
  primary_color: str
  secondary_color: str
  color_filter: str
  text_primary_color: str
  text_secondary_color: str

class UserCharacterResponse(OrmBaseSerializerModel):
  id: UUID
  name: str
  description: str
  code: str
  image_detail: ImageDetail
  skills: List[UserCharacterSkillResponse]

  @classmethod
  def from_orm(cls, user_character: UserCharacter):
    if not user_character:
      return None

    # Create the response model, passing the artist names instead of Artist objects
    return cls(
      id=user_character.id,
      name=user_character.name,
      description=user_character.description,
      code=user_character.code,
      image_detail=ImageDetail(
        background_color=user_character.background_color,
        color_filter=user_character.color_filter,
        primary_color=user_character.primary_color,
        secondary_color=user_character.secondary_color,
        text_primary_color=user_character.text_primary_color,
        text_secondary_color=user_character.text_secondary_color,
      ),
      skills=UserCharacterSkillResponse.from_each_orm(user_character.skills)
    )