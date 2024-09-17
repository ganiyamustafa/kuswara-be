import jwt
import datetime
from core.config import settings

def create_jwt_token(data: dict, secret_key: str, algorithm: str = settings.JWT_ALGORITHM, expires_in: int = settings.JWT_EXPIRES_IN):
    payload = data.copy()

    # skip expired token if expires in is 0
    if expires_in >= 0:
        payload['exp'] = datetime.datetime.utcnow() + datetime.timedelta(seconds=expires_in)

    token = jwt.encode(payload, secret_key, algorithm=algorithm)
    return token

def decode(token: str, secret_key: str, algorithm: str = settings.JWT_ALGORITHM):
    return jwt.decode(token, secret_key, algorithms=algorithm)
