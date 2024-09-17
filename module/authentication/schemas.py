from pydantic import BaseModel

class RegisterSchema(BaseModel):
    name: str
    email: str
    password: str

class LoginSchema(BaseModel):
    name: str
    password: str

class RequestAuthTokenSchema(BaseModel):
  refresh_token: str

class LogoutSchema(BaseModel):
  refresh_token: str