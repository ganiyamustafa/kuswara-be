from sqlalchemy import Column, String, DateTime, func, UniqueConstraint, event, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy_utils import EmailType
from sqlalchemy.orm import relationship
from core.base.models import BaseModel
from fastapi_async_sqlalchemy import db
from module.playlist.models import Playlist
import bcrypt
import uuid
import asyncio

class User(BaseModel):
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)  # Use `String` if `EmailType` is not defined
    password = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())
    user_character_id = Column(UUID(as_uuid=True), ForeignKey('user_characters.id', ondelete="SET NULL"), nullable=True)
    
    # Define relationships
    playlist = relationship('Playlist', uselist=False, back_populates='user')
    user_character = relationship('UserCharacter', uselist=False, back_populates='users')

    __tablename__ = 'users'
    __table_args__ = (
        UniqueConstraint('email', name='uq_email'),
    )

    class Config:
        from_attributes = True

    def __init__(self, name, email, password):
        self.name = name
        self.email = email
        self.set_password(password)

    def __repr__(self):
        return '<User %r>' % self.name
    
    def set_password(self, password):
    # Hash the password and store the hash in the database
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        self.password = hashed.decode('utf-8')

    @staticmethod
    def verify_password(hashed_password, password):
        # Verify the password against the stored hash
        hashed = hashed_password.encode('utf-8')
        return bcrypt.checkpw(password.encode('utf-8'), hashed)

async def _create_playlist_after_create(target: User):
    async with db():
        playlist = Playlist(user_id=target.id)
        db.session.add(playlist)
        await db.session.commit()

def _after_create(mapper, connection, target: User):
    print("============================ playlist created ========================")
    asyncio.create_task(_create_playlist_after_create(target))

event.listen(User, 'after_insert', _after_create)
