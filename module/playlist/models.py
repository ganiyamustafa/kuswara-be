from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship, selectinload
from sqlalchemy.dialects.postgresql import UUID
from core.base.models import BaseModel
from module.song.models import Song
import uuid

class Playlist(BaseModel):
  id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
  user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete="CASCADE"), nullable=False)

  user = relationship('User', back_populates='playlist')
  songs = relationship('Song', secondary='song_playlists', back_populates='playlists', lazy='selectin')

  __tablename__ = 'playlists'

  class Config:
    orm_mode = True
    from_attributes = True

  def __init__(self, user_id):
    self.user_id = user_id

  def __repr__(self):
    return '<Playlist %r>' % self.id

  @staticmethod
  def include_song_artists_scopes(include_artists: bool = False):
    selectinload_q = selectinload(Playlist.songs)
    if include_artists:
      selectinload_q = selectinload_q.selectinload(Song.artists)

    return selectinload_q
