from sqlalchemy import Column, String
from core.base.models import BaseModel

class Authentication(BaseModel):
    token = Column(String, nullable=False, primary_key=True)

    __tablename__ = 'authentications'

    class Config:
        from_attributes = True

    def __init__(self, token):
        self.token = token

    def __repr__(self):
        return '<Authentication %r>' % self.token
