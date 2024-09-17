from fastapi import Request, Response, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from fastapi_async_sqlalchemy import db
from http import HTTPStatus
from helper.response import SuccessResponse, paginate_api
from module.playlist.models import Playlist
from module.song.models import Song
from core.base.serializer_response import MetaResponse
from uuid import UUID

import module.playlist.serializer_responses as serializer
import module.playlist.schemas as schemas

async def add_song_to_playlist(request: Request, response: Response, data: schemas.AddSongToPlaylistSchema):
  playlist = await _get_playlist(request.state.decoded_token['id'])

  if not playlist:
    raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='Playlist Not Found')

  # add songs
  songs = await _get_songs(data.song_ids)
  for song in songs:
    playlist.songs.append(song) if song not in playlist.songs else None
    
  # commit updated data
  await db.session.commit()

  # return response
  response.status_code = HTTPStatus.OK
  return SuccessResponse(serializer.AddSongToPlaylistResponse.from_orm(playlist), None, 'add song to playlist successfully').to_json()

async def remove_song_from_playlist(request: Request, response: Response, data: schemas.RemoveSongFromPlaylistSchema):
  playlist = await _get_playlist(request.state.decoded_token['id'])

  if not playlist:
    raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='Playlist Not Found')

  # remove song
  song_to_remove = next((song for song in playlist.songs if str(song.id) in data.song_ids), None)
  if song_to_remove:
    playlist.songs.remove(song_to_remove)

  await db.session.commit()
  
  # return response
  response.status_code = HTTPStatus.OK
  return SuccessResponse(serializer.RemoveSongFromPlaylistResponse.from_orm(playlist), None, 'remove song from playlist successfully').to_json()

async def get_playlist_songs(request: Request, response: Response):
  # get songs query
  songs_q = select(Song).join(Song.playlists).where(Playlist.user_id == request.state.decoded_token['id']).options(selectinload(Song.artists))
  songs_q, page, limit, count, last_page = await paginate_api(request, songs_q)
  songs = (await db.session.execute(songs_q)).scalars().all()

  # return response
  response.status_code = HTTPStatus.OK
  return SuccessResponse(serializer.SongResponse.from_each_orm(songs), MetaResponse(page=page, limit=limit, total=count, last_page=last_page), 'get songs successfully').to_json()

async def _get_songs(song_ids: list[str]):
  select_q = select(Song).where(Song.id.in_(song_ids))
  return (await db.session.execute(select_q)).scalars().all()

async def _get_playlist(user_id: str, include_song_artists: bool = False):
  select_q = select(Playlist).where(Playlist.user_id == user_id).options(Playlist.include_song_artists_scopes(include_artists=include_song_artists))
  return (await db.session.execute(select_q)).scalar_one_or_none()