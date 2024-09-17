from sqlalchemy import Column, String, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from core.base.models import BaseModel
import uuid

class Song(BaseModel):
  id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
  name = Column(String, nullable=False)
  link = Column(String, nullable=False, unique=True)
  is_cover = Column(Boolean, nullable=True, default=False)
  alternative_names = Column(JSONB, nullable=True)
  seek = Column(String, nullable=False, default="10,30,60")

  artists = relationship('Artist', secondary='song_artists', back_populates='songs')
  playlists = relationship('Playlist', secondary='song_playlists', back_populates='songs')

  __tablename__ = 'songs'

  class Config:
    from_attributes = True

  def __init__(self, name, link, is_cover, alternative_names, seek):
    self.name = name
    self.link = link
    self.is_cover = is_cover
    self.alternative_names = alternative_names
    self.seek = seek

  def __repr__(self):
    return '<Song %r>' % self.name

  @property
  def artist_names(self) -> list[str]:
    # Example function to return a list of artist names
    return [artist.name for artist in self.artists]

  @property
  def seeks(self) -> list[int]:
    # Example function to return a list of artist names
    return [int(seek) for seek in self.seek.split(',')]