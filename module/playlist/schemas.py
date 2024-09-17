from pydantic import BaseModel
from typing import List

class AddSongToPlaylistSchema(BaseModel):
  song_ids: List[str]

class RemoveSongFromPlaylistSchema(BaseModel):
  song_ids: List[str]
  