from jwt import decode as jwt_decode, ExpiredSignatureError, InvalidTokenError
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi import Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from datetime import datetime, timedelta
from apps.auth_app.schemas import TokenData
from jose import JWTError, jwt
from dotenv import load_dotenv
from models import User
from sqlmodel import select
import os
from db import get_session
load_dotenv()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth_2_scheme = OAuth2PasswordBearer(tokenUrl="/api/token")

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


async def get_user(session, username: str):
    result = await session.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()
    return user


async def authenticate_user(session, username: str, password: str):
    user = await get_user(session, username)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user


async def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(session: AsyncSession = Depends(get_session), token: str = Depends(oauth_2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception

    user = await get_user(session, username=token_data.username)
    if user is None:
        raise credentials_exception

    return user


async def create_user(session: AsyncSession, user_data):
    error_list = []
    if user_data.password1 != user_data.password2:
        error_list.append("Passwords do not match")

    if len(user_data.password1) < 8:
        error_list.append("Password must be at least 8 characters")

    if len(user_data.username) < 4:
        error_list.append("Username must be at least 4 characters")

    if user_data.username.isnumeric():
        error_list.append("Username must contain at least one letter")

    # Check if username exists
    username_query = await session.exec(
        select(User).where(User.username == user_data.username.lower())
    )
    existing_username = username_query.one_or_none()
    if existing_username:
        error_list.append("Username already exists")
    
    if error_list:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_list)

    user = User(
        username=user_data.username,
        password=get_password_hash(user_data.password1),
        first_name=user_data.first_name,
        last_name=user_data.last_name,
    )
    session.add(user)
    await session.commit()
    return user


def validate_jwt(token: str):
    try:
        token = token.split("Bearer ")[1]
        payload = jwt_decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if not username:
            raise HTTPException(
                status_code=400, detail="Invalid token: username missing"
            )
        return username
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
