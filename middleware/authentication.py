from typing import Annotated
from fastapi import Header, HTTPException, Request
from helper.jwt import decode
from core.config import settings
from jwt import ExpiredSignatureError

async def verify_token(request: Request, authorization: Annotated[str, Header()]):
    try:
        token = authorization.split('Bearer ')[1]
        request.state.auth_token = token
        request.state.decoded_token = decode(token, settings.AUTH_KEY)
        return
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="token expired")
    except:
        raise HTTPException(status_code=401, detail="invalid token")

