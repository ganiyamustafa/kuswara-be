from fastapi import Request, Response
from fastapi.responses import FileResponse
from module.attachment import constants as constants

import os

async def get_attachment_by_filename(request: Request, response: Response):
  filename = request.path_params.get('filename')
  file_path = os.path.join(constants.STATIC_DIR, filename)
  
  if os.path.exists(file_path):
      return FileResponse(file_path)
  else:
      return {"error": "File not found"}