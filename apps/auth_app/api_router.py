from fastapi import Depends, HTTPException, status, Form
from apps.auth_app.schemas import SignUpForm
from fastapi.routing import APIRouter
from apps.auth_app.schemas import Token
from dotenv import load_dotenv
from apps.auth_app.utils import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    authenticate_user,
    create_access_token,
    create_user,
    get_current_user,
)
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import timedelta
from fastapi import Response
from db import get_session
from models import User
from sqlalchemy.sql import select
load_dotenv()
router = APIRouter()


@router.post("/register")
async def register(
    SignUpForm: SignUpForm, session: AsyncSession = Depends(get_session)
):
    await create_user(session, SignUpForm)
    return Response(status_code=status.HTTP_201_CREATED)


@router.post("/token", response_model=Token)
async def login(
    username: str = Form(...),
    password: str = Form(...),  
    session = Depends(get_session)
    ):
    user = await authenticate_user(session, username, password)
    if not user:
        raise HTTPException(
            status_code=400,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expire = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = await create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expire
    )
    return {"access_token": access_token, "token_type": "Bearer"}


@router.get("/users/me")
async def read_user(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    return {
        "username": current_user.username,
        "first_name": current_user.first_name,
        "last_name": current_user.last_name,
    }

@router.get("/search-username")
async def search_username(
    q: str,
    session: AsyncSession = Depends(get_session)
):
    users = await session.execute(
        select(User).filter(User.username.like(f"%{q}%"))
    )
    users = users.scalars().all()
    users = [{"username": user.username, "id": user.id} for user in users]
    return users
