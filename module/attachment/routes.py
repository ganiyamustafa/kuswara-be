from fastapi import APIRouter
from module.attachment.controllers import get_attachment_by_filename

router = APIRouter()

router.add_api_route('/{filename}', get_attachment_by_filename, methods=['GET'])