from fastapi import APIRouter, Depends
from module.playlist.controllers import add_song_to_playlist, remove_song_from_playlist, get_playlist_songs
from middleware.authentication import verify_token

router = APIRouter()

router.add_api_route('/me/songs', add_song_to_playlist, methods=['POST'], dependencies=[Depends(verify_token)])
router.add_api_route('/me/songs', remove_song_from_playlist, methods=['DELETE'], dependencies=[Depends(verify_token)])
router.add_api_route('/me/songs', get_playlist_songs, methods=['GET'], dependencies=[Depends(verify_token)])