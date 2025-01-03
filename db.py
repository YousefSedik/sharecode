import os
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from dotenv import load_dotenv
from sqlalchemy.orm import sessionmaker

load_dotenv()


def build_pg_url_for_alembic() -> str:
    username = os.environ.get("POSTGRES_USER")
    password = os.environ.get("POSTGRES_PASSWORD")
    server = os.environ.get("POSTGRES_SERVER")
    db = os.environ.get("POSTGRES_DATABASE")
    port = os.environ.get("POSTGRES_PORT")
    if username and password and server and db:
        return f"postgresql://{username}:{password}@{server}:{port}/{db}"
    else:
        raise Exception("Missing environment variables")


def build_pg_url_for_sql() -> str:
    username = os.environ.get("POSTGRES_USER")
    password = os.environ.get("POSTGRES_PASSWORD")
    server = os.environ.get("POSTGRES_SERVER")
    db = os.environ.get("POSTGRES_DATABASE")
    port = os.environ.get("POSTGRES_PORT")
    if username and password and server and db and port:
        return f"postgresql+asyncpg://{username}:{password}@{server}:{port}/{db}"
    else:
        raise Exception("Missing environment variables")


DATABASE_URL = build_pg_url_for_sql()

engine = create_async_engine(DATABASE_URL, echo=False, future=True)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

async def get_session() -> AsyncSession:
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session
