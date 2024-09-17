from core.base.serializer_response import OrmBaseSerializerModel
from typing import List
from uuid import UUID
from module.song.serializer_response import SongResponse

class AddSongToPlaylistResponse(OrmBaseSerializerModel):
  id: UUID

class RemoveSongFromPlaylistResponse(OrmBaseSerializerModel):
  id: UUID