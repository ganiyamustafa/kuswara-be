from pydantic import BaseModel
from typing import Optional, List

class SkillSchemas(BaseModel):
  cooldown: int
  description: str
  icon: str
  is_active: bool
  name: str
  skill_type: int

class UserCharacterSchemas(BaseModel):
  id: str
  name: str
  image: str
  background_image: Optional[str] = None
  skills: Optional[List[SkillSchemas]] = None
  code: str

class ParticipantSchemas(BaseModel):
  id: str
  answer: Optional[str] = None
  artists_answer: Optional[List[str]] = []
  is_room_master: bool
  is_skip_answer: bool
  is_skip_song: bool
  point: int
  song_count: int
  user_character: Optional[UserCharacterSchemas] = None

  def id_key(self):
    if self.id == '0000-0000-0000': 
      return self.id

    return self.id.replace('-', '_')

class SongSchemas(BaseModel):
  name: str
  alternative_names: Optional[List[str]] = []
  artists: Optional[List[str]] = None
  index: int
  seek: int
  start_from_seek: int
  total: int
  url: str

class RoomSchemas(BaseModel):
  name: str
  password: str
  time_limit: int
  type: int
  phase: int
  is_all_listened_song: bool
  is_all_listened_artists: bool
  allow_cover: bool
  song_distribution: int
  played_song_ids: List[str]

class GameRoomSchemas(BaseModel):
  id: str
  room: RoomSchemas
  participants: List[ParticipantSchemas]
  song: SongSchemas

  def participant_ids(self) -> list[str]:
    return [participant.id for participant in self.participants if participant.id != "0000-0000-0000"] # ['4c237822_342a_43e7_8f0a_8c3ae6a83da7', 'f3c84be9-17ad-4623-83af-ead1541c470a']

  def song_count(self) -> dict:
    song_count_dict = {}
    for participant in self.participants:
      if participant.id != '0000-0000-0000':
        song_count_dict[participant.id] = participant.song_count
      
    return song_count_dict

  @classmethod
  def from_dict(self, dict: dict, id: str):
    return self(
      id = id,
      room = RoomSchemas(**dict['room']),
      participants = self._participants_from_dict(dict),
      song = SongSchemas(**dict['song'])
    )

  @staticmethod
  def _participants_from_dict(dict: dict) -> list[ParticipantSchemas]:
    participants = []

    for key, val in dict.items():
      if key == 'participants':
        for id, participant in val.items():
          id = id.replace('_', '-')
          participants.append(ParticipantSchemas(**participant, id=id))

    return participants