from datetime import datetime, timedelta, timezone

import jwt
from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from pydantic import BaseModel

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="user/token")
SECRET_KEY = "198fbe5f5dee8a085d8c212a3531c2c20a07fd53407d97ec32b8102c32978293"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

CREDENTIALS_EXCEPTION = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

class Token(BaseModel):
    access_token: str

def create_access_token(id: str):
    to_encode = { "sub": id }
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    expire = datetime.now(timezone.utc) + access_token_expires
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print(payload)
        userid: str = payload.get("sub")
        print(userid)
        if userid is None:
            return None
        return userid
    except InvalidTokenError:
        return None
    
    
