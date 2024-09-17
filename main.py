from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_async_sqlalchemy import SQLAlchemyMiddleware
from fastapi.staticfiles import StaticFiles
from core import config
from middleware.log import LoggingMiddleware
import uvicorn

from module.user.routes import router as user_routes
from module.authentication.routes import router as token_router
from module.song.routes import router as song_router
from module.artist.routes import router as artist_router
from module.playlist.routes import router as playlist_router
from module.game.routes import router as game_router
from module.attachment.routes import router as attachment_router

from firebase_admin import credentials, initialize_app

import os

# initialize firebase
cred = credentials.Certificate(config.settings.FIREBASE_KEY_FILENAME)
initialize_app(cred)

# App outside of name == main for dynamic import by hot reload worker
app = FastAPI(title=config.settings.PROJECT_NAME, root_path='/api/v1')
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

app.add_middleware(
    SQLAlchemyMiddleware,
    db_url=config.settings.ASYNC_DATABASE_URI,
    engine_args={              # engine arguments example
        'echo': True,          # print all SQL statements
        'pool_pre_ping': True, # feature will normally emit SQL equivalent to “SELECT 1” each time a connection is checked out from the pool
        'pool_size': 5,        # number of connections to keep open at a time
        'max_overflow': 10,    # number of connections to allow to be opened above pool_size
        'connect_args': {
            'prepared_statement_cache_size': 0,  # disable prepared statement cache
            'statement_cache_size': 0,           # disable statement cache
        },
    },
)

app.add_middleware(LoggingMiddleware)
app.include_router(user_routes, prefix='/users')
app.include_router(token_router, prefix='/authentications')
app.include_router(song_router, prefix='/songs')
app.include_router(artist_router, prefix='/artists')
app.include_router(playlist_router, prefix='/playlists')
app.include_router(game_router, prefix='/games')
app.include_router(attachment_router, prefix='/attachments')

if __name__ == '__main__':
  uvicorn.run('main:app', host='0.0.0.0', port=config.settings.PROJECT_PORT, reload=True)
        