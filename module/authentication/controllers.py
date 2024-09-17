from sqlalchemy import select, or_, delete, and_
from sqlalchemy.exc import IntegrityError
from fastapi import Request, Response, HTTPException
from fastapi_async_sqlalchemy import db
from http import HTTPStatus
from core.config import settings
from helper.response import SuccessResponse
from module.authentication.models import Authentication
from module.user.models import User
from module.authentication import schemas
from helper import jwt

import module.authentication.serializer_responses as serializer

async def request_auth_token(request: Request, response: Response, data: schemas.RequestAuthTokenSchema):
  # validate refresh token
  await _check_token_exists(data.refresh_token)

  # decode refresh token
  try:
    decoded_token = jwt.decode(data.refresh_token, settings.REFRESH_KEY)
  except:
    raise HTTPException(status_code=401, detail='invalid token')

  # create token
  auth_token = jwt.create_jwt_token(decoded_token, settings.AUTH_KEY)

  # return response
  response.status_code = HTTPStatus.OK
  return SuccessResponse(serializer.RequestTokenResponse(auth_token=auth_token), None, "request successfully").to_json()

async def register(request: Request, response: Response, data: schemas.RegisterSchema):
  check_exists_statement = select(User).where(
    or_(
      User.email == data.email,
      User.name == data.name,
    )
  )
  user_exists = await db.session.execute(check_exists_statement)

  if user_exists.first():
      raise HTTPException(status_code=HTTPStatus.CONFLICT, detail='users with email or name already exists')
        
  # save user
  user = _save_user(data)
  await db.session.commit()
  await db.session.refresh(user)

  response.status_code = HTTPStatus.CREATED
  
  return SuccessResponse(serializer.RegisterResponse.from_orm(user), None, 'user created successfully').to_json()

async def login(request: Request, response: Response, data: schemas.LoginSchema):
  check_exists_statement = select(User).where(User.name == data.name)
  user_exists = await db.session.execute(check_exists_statement)
  user = user_exists.first()

  # validate user
  if not user or not User.verify_password(user[0].password, data.password):
    raise HTTPException(status_code=401, detail='invalid username or password')

  user = user[0]

  # create token
  auth_token = jwt.create_jwt_token(serializer.UserJWT.from_orm(user).dict(), settings.AUTH_KEY)
  refresh_token = jwt.create_jwt_token(serializer.UserJWT.from_orm(user).dict(), settings.REFRESH_KEY, expires_in=-1)

  # save refresh token
  await _save_refresh_token(refresh_token)

  # return response
  response.status_code = HTTPStatus.OK
  return SuccessResponse(serializer.LoginResponse(auth_token=auth_token, refresh_token=refresh_token), None, "login successfully").to_json()

async def logout(request: Request, response: Response, data: schemas.LogoutSchema):
  # delete token
  deleted_galleries_q = delete(Authentication).where(
    Authentication.token == data.refresh_token,
  )
  await db.session.execute(deleted_galleries_q)
  await db.session.commit()

  # return response
  response.status_code = HTTPStatus.OK
  return SuccessResponse(None, None, "logout successfully").to_json()

async def _save_refresh_token(refresh_token: str):
  try:
    token = Authentication(refresh_token)
    db.session.add(token)
    await db.session.commit()
  except IntegrityError as e:
    if 'unique constraint' in str(e.orig):
      await db.session.rollback()

def _save_user(data: schemas.RegisterSchema):
  user = User(**data.dict())
  db.session.add(user)
  
  return user

async def _check_token_exists(refresh_token: str):
  check_exists_statement = select(Authentication).where(Authentication.token == refresh_token)
  token_exists = await db.session.execute(check_exists_statement)
  token = token_exists.first()

  # validate user
  if not token:
    raise HTTPException(status_code=401, detail='invalid token')

  return token[0]