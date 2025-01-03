from fastapi.routing import APIRouter
from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from db import get_session
from models import User
from datetime import timedelta
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()
