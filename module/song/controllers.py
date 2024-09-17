from fastapi import Request, Response, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import selectinload, load_only
from fastapi_async_sqlalchemy import db
from module.song import schemas
from helper.response import SuccessResponse
from module.song.models import Song
from module.artist.models import Artist
from http import HTTPStatus
from core.config import settings

import module.song.serializer_response as serializer
import requests
import json

async def check_song(request: Request, response: Response, data: schemas.CheckSongSchema):
  song = await _get_existing_song(data.link)

  if not song:
    raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='song not found')

  response.status_code = HTTPStatus.OK
  return SuccessResponse(serializer.SongResponse.from_orm(song), None, "get song successfully").to_json()

async def get_song_names(request: Request, response: Response):
  # get all song names
  songs = await _get_all_song_names()
  song_names = []
  
  # loop and append song name to list
  for song in songs:
    song_names.append(song.name)
    song_names += song.alternative_names or []

  # remove duplicate name
  song_names = list(set(song_names))

  # return
  response.status_code = HTTPStatus.OK
  return SuccessResponse(song_names, None, "get song successfully").to_json()

async def add_song(request: Request, response: Response, data: schemas.AddSongSchema):
  song = await _get_existing_song(data.link)

  if song:
    raise HTTPException(status_code=HTTPStatus.CONFLICT, detail='song with this link already exists')

  # check link
  if not data.link.startswith('https://music.youtube.com'):
    raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail='currently only support link from youtube music')

  # format link
  data.link = data.link.split('&')[0]

  # save song
  song = Song(**data.dict())

  # save artists
  song.artists = await _get_song_artists_data(data)

  db.session.add(song)
  await db.session.commit()
  # await db.session.refresh(song)

  response.status_code = HTTPStatus.CREATED
  return SuccessResponse(serializer.SongResponse.from_orm(song), None, "add song successfully").to_json()

async def report_song(request: Request, response: Response, data: schemas.AddSongSchema):
  song = await _get_existing_song(data.link)

  if not song:
    raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='song not found')

  # send discord webhook 
  await _send_reported_song_webhook(song, data)

  response.status_code = HTTPStatus.OK
  return SuccessResponse(None, None, "report song successfully").to_json()

async def _get_song_artists_data(data: schemas.AddSongSchema):
  existing_artists = await _get_existing_artists(data.artists)
  existing_artist_names = {artist.name for artist in existing_artists}
  return [Artist(name=artist) for artist in data.artists if artist not in existing_artist_names] + existing_artists

async def _get_existing_artists(artists: list[str]):
  check_exists_q = select(Artist).where(Artist.name.in_(artists))
  return (await db.session.execute(check_exists_q)).scalars().all()

async def _get_all_song_names() -> list[Song]:
  song_q = select(Song).distinct(Song.name, Song.alternative_names).options(load_only(Song.name, Song.alternative_names))
  return (await db.session.execute(song_q)).scalars().all()

async def _get_existing_song(link: str):
  check_exists_q = select(Song).where(Song.link == link).options(selectinload(Song.artists))
  song_exists = await db.session.execute(check_exists_q)
  return song_exists.scalar_one_or_none()

async def _send_reported_song_webhook(song: Song, req_song: schemas.AddSongSchema):
  json_reported_song = json.dumps(serializer.SongResponse.from_orm(song).dict(), indent=4)
  json_new_song = json.dumps(serializer.SongResponse(**req_song.dict(), artists=req_song.artists).dict(), indent=4)
  await _send_webhook_discord('Song Reported', f'\n**=== Reported Data ===**\n\n{json_reported_song}\n\n**=== New Data ===**\n\n{json_new_song}')

async def _send_webhook_discord(title: str, desc: str):
  payload = {
    'embeds': [
      {
        'title': title,
        'description': desc,
        'color': 0xff0000 
      }
    ]
  }

  res = requests.post(settings.SONG_REPORTED_WEBHOOK, json=payload)