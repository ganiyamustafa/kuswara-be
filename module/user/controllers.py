from fastapi import Request, Response, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import selectinload, load_only
from fastapi_async_sqlalchemy import db
from helper.response import SuccessResponse
from module.user.models import User
from module.user_character.models import UserCharacter
from http import HTTPStatus

import module.user.serializer_responses as serializer

async def get_my_profile(request: Request, response: Response):
  user = await _get_user(request.state.decoded_token['id'])

  if not user:
    raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='user not found')

  response.status_code = HTTPStatus.OK
  return SuccessResponse(serializer.UserResponse.from_orm(user), None, "get user successfully").to_json()

async def _get_user(id: str) -> User:
  user_q = select(User).where(User.id == id).options(selectinload(User.user_character).options(selectinload(UserCharacter.skills)))
  return (await db.session.execute(user_q)).scalar_one_or_none()