from fastapi import Request, Response
from core.firebase import firebase
from module.game.schemas import GameRoomSchemas, ParticipantSchemas
from module.game import constants
from module.song.models import Song
from module.playlist.models import Playlist
from module.artist.models import Artist
from helper.youtube import youtube_to_mp3
from sqlalchemy import select, func, or_, and_
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import selectinload
from fastapi_async_sqlalchemy import db
from datetime import datetime
from typing import Tuple, Optional
from helper.func import time_check
import character.constants as chr_constants
import character

import asyncio
import uuid
import random
import time
import os

_loop = asyncio.get_event_loop()

async def listen_game_room(request: Request, response: Response):
  room_id = request.path_params.get('id')
  room = firebase.collection('game_rooms').document(room_id)
  room.on_snapshot(_listen_room)

def _listen_room(doc_snapshot, changes, read_time):
  for doc in doc_snapshot:
    game_room = GameRoomSchemas.from_dict(doc.to_dict(), doc.id)
    
  if game_room.song.index < game_room.song.total and game_room.room.phase not in [constants.RoomPhase.LOBBY.value, constants.RoomPhase.PREPARED_FIRST_SONG.value, constants.RoomPhase.WAITING_FIRST_SONG.value]:
    # calculate point when participants have been answered
    _calculate_point(game_room)

    # next song function
    asyncio.run_coroutine_threadsafe(_next_song(game_room), _loop)

    # update seek of song
    _update_seek_song(game_room)
  elif game_room.room.phase in [constants.RoomPhase.PREPARED_FIRST_SONG.value, constants.RoomPhase.WAITING_FIRST_SONG.value]:
    # prepared first song
    asyncio.run_coroutine_threadsafe(_next_song(game_room), _loop)
  else:
    # end game if total song has reached maximum
    _end_game(game_room)

def _update_seek_song(game_room: GameRoomSchemas):
  # delay for 1 second
  time.sleep(1)

  # get game room data in real time
  game_room = _get_game_room_from_firebase(game_room.id)

  # check if room phase is not in lobby or prepared first song
  if game_room.room.phase not in [constants.RoomPhase.LOBBY, constants.RoomPhase.LOBBY.value, constants.RoomPhase.PREPARED_FIRST_SONG.value]:
    # update song seek data
    updated_data = {'song.seek': game_room.song.seek + 1}

    # update room
    _update_game_room(updated_data, game_room.id)

def _calculate_point(game_room: GameRoomSchemas):
  # get game room data in real time
  game_room = _get_game_room_from_firebase(game_room.id)

  is_not_all_skip = [False for participant in game_room.participants if not participant.is_skip_answer]
  song = game_room.song
  room = game_room.room

  # check if all user skip or song time is more than limit time
  song_time = song.seek - song.start_from_seek
  if not is_not_all_skip or song_time >= room.time_limit-1 and room.phase == constants.RoomPhase.ANSWER.value:
    update_point_data = {'room.phase': constants.RoomPhase.LISTEN_SONG.value, 'song.seek': song.start_from_seek}

    # init all point for skill param
    point_calculation = {}
    activated_skill_list: list[str] = []

    # check answer
    for participant in game_room.participants:
      # add activated skill to list
      if participant.user_character and participant.user_character.skills:
        for skill in participant.user_character.skills and skill.skill_type == chr_constants.SkillType.POINT_MANIPULATION.value:
          activated_skill_list.append(f'${participant.user_character.code}.${skill.name}')

      # init calculation point for every participant
      point_calculation[participant.id] = 0

      # init correct type
      answer_song_correctly = False

      # set point base value
      update_point_data[f'participants.{participant.id_key()}.point'] = participant.point

      # update point on song answer correctly
      if participant.answer and participant.answer.lower() in ([song.name.lower()] + [answer.lower() for answer in song.alternative_names or []]):
        point_calculation[participant.id] += constants.SONG_POINT

        # calculate point
        update_point_data[f'participants.{participant.id_key()}.point'] += constants.SONG_POINT

        # set correct type
        answer_song_correctly = True
      
      # update point on song artists answer correctly
      if game_room.room.type == constants.RoomType.SONG_ARTIST.value:
        point, answer_correct_artists_type = _calculate_song_artist_point(game_room, participant)
        update_point_data[f'participants.{participant.id_key()}.point'] += point

        point_calculation[participant.id] += point

      # set answer correct type data
      update_point_data[f'participants.{participant.id_key()}.answer_correctly_type'] = _get_answer_correct_type(answer_song_correctly, answer_correct_artists_type)

      # reset answer value
      update_point_data.update(_clear_participants_data(game_room.participants))

    # exec skill function to update point data
    for skill in activated_skill_list:
      exec(f'update_point_data = character.${skill}(game_room, point_calculation, update_point_data)')

    _update_game_room(update_point_data, game_room.id)

def _get_answer_correct_type(answer_song_correctly: bool, answer_artists_correct_type: int) -> int:
  if answer_song_correctly and answer_artists_correct_type == constants.AnswerCorrectType.CORRECT.value:
    return constants.AnswerCorrectType.CORRECT.value
  elif answer_song_correctly or answer_artists_correct_type in [constants.AnswerCorrectType.CORRECT.value, constants.AnswerCorrectType.HALF_CORRECT.value]:
    return constants.AnswerCorrectType.HALF_CORRECT.value
  else:
    return constants.AnswerCorrectType.WRONG.value

def _calculate_song_artist_point(game_room: GameRoomSchemas, participant: ParticipantSchemas):
  correct_answer = [answer.lower() for answer in game_room.song.artists or []]
  participant_answer = [answer.lower() for answer in participant.artists_answer or []]

  # get correct participant answer
  correct_participant_answer = set(correct_answer) & set(participant_answer)

  # get len diff between participant answer and correct participant answer
  participant_answer_diff_len = len(participant_answer) - len(correct_participant_answer)

  # get total incorrect answer
  # 0 if participant_answer_diff_len is less or equal then 0 or total of correct answer is total of participant answer
  # total of participant answer - correct participant answer if above then 0
  incorrect_participant_answer_len = 0 if (participant_answer_diff_len <= 0 or len(participant_answer) <= len(correct_answer)) else participant_answer_diff_len

  # set correct tyoe
  # correct if all answers is correct
  # half correct if at least one of answers is correct
  # wrong if all incorrect
  answer_correct_type = constants.AnswerCorrectType.WRONG.value
  if len(correct_answer) == len(correct_participant_answer):
    answer_correct_type = constants.AnswerCorrectType.CORRECT.value
  elif len(correct_answer) > len(correct_participant_answer) and len(correct_participant_answer) > 0:
    answer_correct_type = constants.AnswerCorrectType.HALF_CORRECT.value

  return (len(correct_participant_answer) * constants.ARTIST_POINT) - (incorrect_participant_answer_len * constants.ARTIST_POINT), answer_correct_type

async def _next_song(game_room: GameRoomSchemas):
  # get game room data in real time
  game_room = _get_game_room_from_firebase(game_room.id)

  room, song = game_room.room, game_room.song
  is_not_all_skip = [False for participant in game_room.participants if not participant.is_skip_song]

  song_time = song.seek - song.start_from_seek

  # execute if:
  # room phase is listen song (2)
  # all participants skip song phase and or song time is more than end time
  if room.phase == constants.RoomPhase.PREPARED_FIRST_SONG.value or (room.phase == constants.RoomPhase.LISTEN_SONG.value and (
    (not is_not_all_skip and song_time+constants.SONG_PHASE_SKIP_SECOND >= constants.SONG_PHASE_DURATION_SECOND) or (song_time >= constants.SONG_PHASE_DURATION_SECOND-10)
  )):

    # end game if total song has reached
    if (song.index >= song.total):
      return _end_game(game_room)

    # update to room phase
    _update_room_phase_when_waiting_song(game_room)
    
    try:
      song_data, participant_turn = await _get_song_data(game_room)

      # return empty if song not found
      if not song_data:
        return

      # start = datetime.now()
      def _load_song():
        try:
          return youtube_to_mp3(song_data.link)
        except:
          return _load_song()

      song_url = _load_song()
      # end = datetime.now()
      # print((end - start).total_seconds())

      # append played song id
      room.played_song_ids.append(str(song_data.id))

      # set song seek
      seek = random.choice(song_data.seeks)

      # update next song data
      update_data = {
        'song.url': song_url,
        'song.index': song.index+1,
        'song.seek': seek,
        'song.start_from_seek': seek,
        'song.name': song_data.name,
        'song.alternative_names': song_data.alternative_names,
        'song.artists': song_data.artist_names,
        'room.phase': constants.RoomPhase.ANSWER.value,
        'room.played_song_ids': room.played_song_ids
      }

      # reset skip song data
      for participant in game_room.participants:
        # reset skip song value
        update_data[f'participants.{participant.id_key()}.is_skip_song'] = False

        # reset answer correct type value
        update_data[f'participants.{participant.id_key()}.answer_correctly_type'] = constants.AnswerCorrectType.IDLE.value

        # reset answer value
        update_data[f'participants.{participant.id_key()}.artists_answer'] = []
        update_data[f'participants.{participant.id_key()}.answer'] = None

        # update participant song count
        if participant.id == participant_turn:
          update_data[f'participants.{participant.id_key()}.song_count'] = participant.song_count + 1

      # update game room data
      _update_game_room(update_data, game_room.id)
    except Exception as e:
      # os.environ['next_song'] = 'completed'
      print('error', e)

def _update_room_phase_when_waiting_song(game_room: GameRoomSchemas):
  # update room phase to waiting next song if current phase is not prepared first song else update to waiting first song
  update_room_phase_data = {'room.phase': constants.RoomPhase.WAITING_NEXT_SONG.value}
  if game_room.room.phase == constants.RoomPhase.PREPARED_FIRST_SONG.value:
    update_room_phase_data['room.phase'] = constants.RoomPhase.WAITING_FIRST_SONG.value

  _update_game_room(update_room_phase_data, game_room.id)

def _update_game_room(update_data: dict, room_id: str):
  firebase.collection('game_rooms').document(room_id).update(update_data)

async def _get_song_data(game_room: GameRoomSchemas) -> Tuple[Song | None, str]:
  # init data
  group_by_q = [Song.id]
  room = game_room.room

  # group by artists id when is_all_listened_artists config is true
  if room.is_all_listened_artists and len(game_room.participant_ids()) > 1:
    group_by_q.append(Artist.id)

  song_q = select(Song).join(Song.playlists).join(Song.artists).where(
    Playlist.user_id.in_(game_room.participant_ids())
  ).group_by(*group_by_q).distinct()

  # get song when the song is not have been played
  if room.played_song_ids:
    song_q = song_q.where(Song.id.notin_(room.played_song_ids))

  # get data with more then 1 count when is_all_listened_song is true
  if room.is_all_listened_song:
    song_q = song_q.having(func.count(Song.id) >= len(game_room.participant_ids()))

  # convert song_q to subquery
  song_cte_q = song_q.cte('song_cte')

  # create new song_q
  song_q = select(Song)

  # get cover song and join sub query
  if room.allow_cover:
    song_q = song_q.where(or_(
      Song.name.in_(select(song_cte_q.c.name)), 
      Song.alternative_names.contains(func.jsonb_build_array(song_cte_q.c.name)),
      Song.alternative_names.contains(song_cte_q.c.alternative_names),
    ))
  else:
    song_q = song_q.join(song_cte_q, Song.id == song_cte_q.c.id).where(Song.is_cover == False)

  # get participant turn
  participant_turns = _get_participant_song_turn(game_room)

  for participant_turn in participant_turns:
    # eager load artists
    song_q = song_q.order_by(func.random()).join(Song.playlists).where(
      and_(
        Playlist.user_id == participant_turn,
        Song.id.in_((select(song_cte_q.c.id)))
      )).options(selectinload(Song.artists)).limit(1)

    # exec query
    async with db():
      song_data = (await db.session.execute(song_q)).scalar_one_or_none()

    # break if song has data
    if song_data:
      break

  # end game if not any player have song left
  if not song_data:
    _end_game(game_room)

  return song_data, participant_turn

def _end_game(game_room: GameRoomSchemas):
  # reset room data
  updated_data = {
    'room.phase': constants.RoomPhase.LOBBY.value,
    'room.played_song_ids': [],
    'song.index': 0
  }

  # reset participants data
  updated_data.update(_clear_participants_data(game_room.participants, end_game=True))
  
  # update data
  _update_game_room(updated_data, game_room.id)  

def _clear_participants_data(participants: list[ParticipantSchemas], end_game: bool = False):
  update_participant_datas = {}
  for participant in participants:
    update_participant_datas[f'participants.{participant.id_key()}.is_skip_answer'] = False
    update_participant_datas[f'participants.{participant.id_key()}.is_skip_song'] = False

    if end_game:
      update_participant_datas[f'participants.{participant.id_key()}.artists_answer'] = []
      update_participant_datas[f'participants.{participant.id_key()}.answer'] = None
      update_participant_datas[f'participants.{participant.id_key()}.point'] = 0
      update_participant_datas[f'participants.{participant.id_key()}.song_count'] = 0

  return update_participant_datas

def _get_participant_song_turn(game_room: GameRoomSchemas) -> list[str]:
  if game_room.room.song_distribution == constants.SongDistribution.EQUAL.value:
    return _get_participant_song_turn_equal(game_room)
  elif game_room.room.song_distribution == constants.SongDistribution.RANDOM.value:
    return _get_participant_song_turn_random(game_room)

def _get_participant_song_turn_equal(game_room: GameRoomSchemas) -> list[str]:
  song_total = game_room.song.total
  song_count = game_room.song_count()
  count_total = sum(song_count.values())
  total_song_distribution_per_participant = _get_total_song_distribution_per_participant(game_room)

  # get turn
  
  if count_total < song_total:
    # get random turn
    participant_turns = _get_participant_song_turn_random(game_room)
    for participant_turn in participant_turns.copy():
      if song_count[participant_turn] > total_song_distribution_per_participant[participant_turn]:
        # remove participant id from list where maximum song count has reached
        participant_turns.remove(participant_turn)
  
    return participant_turns
  
  return [str(uuid.uuid4())]

def _get_total_song_distribution_per_participant(game_room: GameRoomSchemas) -> dict:
  # initialize data
  total_song = game_room.song.total
  participant_ids = game_room.participant_ids()
  total_participant = len(participant_ids)

  # get how much song will participant hold
  total_base_song_per_participant = total_song // total_participant

  # get how much participant who get extra song
  total_extra_song_for_participant = total_song % total_participant

  # calculate total song per participant
  total_song_per_participant = [total_base_song_per_participant + 1] * total_extra_song_for_participant + [total_base_song_per_participant] * (total_participant - total_extra_song_for_participant)

  # convert to dict
  song_distribution = {}
  for idx, participant_id in enumerate(participant_ids):
    song_distribution[participant_id] = total_song_per_participant[idx]

  return song_distribution

def _get_participant_song_turn_random(game_room: GameRoomSchemas, exclude_participants: list[str] = []) -> list[str]:
  participant_turns = [participant_id for participant_id in game_room.participant_ids() if participant_id not in exclude_participants]
  random.shuffle(participant_turns)
  return participant_turns

def _get_game_room_from_firebase(id: str) -> GameRoomSchemas:
  return GameRoomSchemas.from_dict(firebase.collection('game_rooms').document(id).get().to_dict(), id)