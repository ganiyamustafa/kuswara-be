from fastapi import APIRouter, Depends
from module.song.controllers import check_song, add_song, report_song, get_song_names
from middleware.authentication import verify_token

router = APIRouter()

router.add_api_route('', add_song, methods=['POST'], dependencies=[Depends(verify_token)])
router.add_api_route('/names', get_song_names, methods=['GET'], dependencies=[Depends(verify_token)])
router.add_api_route('/check', check_song, methods=['POST'], dependencies=[Depends(verify_token)])
router.add_api_route('/report', report_song, methods=['POST'], dependencies=[Depends(verify_token)])