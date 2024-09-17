from fastapi import APIRouter, Depends
from module.artist.controllers import get_artist_names
from middleware.authentication import verify_token

router = APIRouter()

router.add_api_route('/names', get_artist_names, methods=['GET'], dependencies=[Depends(verify_token)])