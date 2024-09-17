from core.base.serializer_response import OrmBaseSerializerModel
from typing import List, Optional
from uuid import UUID

class SongResponse(OrmBaseSerializerModel):
    id: Optional[UUID] = None
    name: str
    artists: List[str]
    link: str
    is_cover: bool

    @classmethod
    def from_orm(cls, song):
        # Convert the list of Artist objects to a list of artist names
        artists_names = [artist.name for artist in song.artists]

        # Create the response model, passing the artist names instead of Artist objects
        return cls(
            id=song.id,
            name=song.name,
            link=song.link,
            artists=artists_names,
            is_cover=song.is_cover
        )

    @classmethod
    def from_each_orm(cls, songs):
        return [cls.from_orm(song) for song in songs]