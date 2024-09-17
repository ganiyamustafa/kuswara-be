from fastapi import Request, Response
from sqlalchemy import select
from sqlalchemy.orm import load_only
from fastapi_async_sqlalchemy import db
from helper.response import SuccessResponse
from module.artist.models import Artist
from http import HTTPStatus
from core.config import settings

async def get_artist_names(request: Request, response: Response):
  # get all song names
  artists = await _get_all_artists_names()
  artist_names = []
  
  # loop and append song name to list
  for artist in artists:
    artist_names.append(artist.name)

  # remove duplicate name
  artist_names = list(set(artist_names))

  # return
  response.status_code = HTTPStatus.OK
  return SuccessResponse(artist_names, None, "get artist successfully").to_json()

async def _get_all_artists_names() -> list[Artist]:
  artist_q = select(Artist).distinct(Artist.name).options(load_only(Artist.name))
  return (await db.session.execute(artist_q)).scalars().all()