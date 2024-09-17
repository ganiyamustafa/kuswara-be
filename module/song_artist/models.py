from sqlalchemy import Column, UUID, ForeignKey
from sqlalchemy.orm import relationship
from core.base.models import BaseModel
import uuid

class SongArtist(BaseModel):
  id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
  artist_id = Column(UUID(as_uuid=True), ForeignKey('artists.id', ondelete="CASCADE"))
  song_id = Column(UUID(as_uuid=True), ForeignKey('songs.id', ondelete="CASCADE"))

  __tablename__ = 'song_artists'

  def __init__(self, hospital_facility_id, hospital_id):
      self.hospital_facility_id = hospital_facility_id
      self.hospital_id = hospital_id

  def __repr__(self):
      return '<SongArtist %r>' % self.id