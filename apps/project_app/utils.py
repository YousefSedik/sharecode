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
