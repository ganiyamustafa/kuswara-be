from fastapi import APIRouter, Depends
from module.user.controllers import get_my_profile
from middleware.authentication import verify_token

router = APIRouter()
router.add_api_route('/me', get_my_profile, methods=['GET'], dependencies=[Depends(verify_token)])