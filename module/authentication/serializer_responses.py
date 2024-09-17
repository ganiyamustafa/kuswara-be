from core.base.serializer_response import OrmBaseSerializerModel
from uuid import UUID

class RequestTokenResponse(OrmBaseSerializerModel):
  auth_token: str

class RegisterResponse(OrmBaseSerializerModel):
    id: UUID

class LoginResponse(OrmBaseSerializerModel):
    auth_token: str
    refresh_token: str

class UserJWT(OrmBaseSerializerModel):
    id: UUID
    name: str
    email: str