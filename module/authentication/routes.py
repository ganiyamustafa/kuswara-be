from fastapi import APIRouter
from module.authentication.controllers import request_auth_token, register, login, logout


router = APIRouter()

router.add_api_route('/auth-token/request', request_auth_token, methods=['POST'])
router.add_api_route('/register', register, methods=['POST'])
router.add_api_route('/login', login, methods=['POST'])
router.add_api_route('/logout', logout, methods=['POST'])