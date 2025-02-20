from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timezone, timedelta
from fastapi import Depends, HTTPException
from passlib.context import CryptContext # type:ignore
from sqlmodel import Session
import jwt
import os

from models import TokenData, Users
from db import get_session

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='login', scheme_name="UserLogin")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str):
    return pwd_context.hash(password)

def verify(plain_password: str, hashed_password: str):     
  return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_access_token(token: str, credentials_exception):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        id = str(payload.get("user_id"))
        if id is None:
            raise credentials_exception
        token_data = TokenData(id=id)
        return token_data
    except jwt.InvalidTokenError:  # Catch any JWT-related errors
        raise credentials_exception

def get_current_user(token: str = Depends(oauth2_scheme), session: Session = Depends(get_session)):
    credentials_exception = HTTPException(
        status_code=403, 
        detail=f"Could not validate credentials", 
        headers={"WWW-Authenticate": "Bearer"})
    token_data = verify_access_token(token, credentials_exception)
    # user = session.exec(select(Users).where(Users.id == int(token_data.id))).first()
    user = session.get(Users, int(token_data.id))
    if user is None:
        raise credentials_exception
    return user