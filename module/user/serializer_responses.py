from uuid import UUID
from core.base.serializer_response import OrmBaseSerializerModel
from typing import Optional
from module.user_character.serializer_responses import UserCharacterResponse
from module.user.models import User

class UserResponse(OrmBaseSerializerModel):
    id: UUID
    name: str
    user_character: Optional[UserCharacterResponse] = None

    @classmethod
    def from_orm(cls, user: User):
        # Create the response model, passing the artist names instead of Artist objects
        return cls(
            id=user.id,
            name=user.name,
            user_character=UserCharacterResponse.from_orm(user.user_character)
        )

    # @classmethod
    # def from_each_orm(cls, songs):
    #     return [cls.from_orm(song) for song in songs]