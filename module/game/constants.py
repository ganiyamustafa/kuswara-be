from enum import Enum

SONG_POINT = 10
ARTIST_POINT = 5
SONG_PHASE_DURATION_SECOND = 30
SONG_PHASE_SKIP_SECOND = 20

class RoomType(Enum):
  NORMAL = 0
  SONG_ARTIST = 1

class RoomPhase(Enum):
  ANSWER = 0
  LISTEN_SONG = 1
  LOBBY = 2
  PREPARED_FIRST_SONG = 3
  WAITING_NEXT_SONG = 4
  LAST_STANDING = 5
  WAITING_FIRST_SONG = 6

class SongDistribution(Enum):
  EQUAL = 0
  RANDOM = 1

class AnswerCorrectType(Enum):
  IDLE = 0
  CORRECT = 1
  WRONG = 2
  HALF_CORRECT = 3