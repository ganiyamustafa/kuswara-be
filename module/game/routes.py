from fastapi import APIRouter, Depends
from module.game.controllers import listen_game_room
from middleware.authentication import verify_token

router = APIRouter()

router.add_api_route('/{id}/listen', listen_game_room, methods=['POST'], dependencies=[Depends(verify_token)])