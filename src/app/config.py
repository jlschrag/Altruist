from typing import Optional

from fastapi import Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from dal import MetricsDAL, RedisDAL
from schemas import AuthToken
from service import MetricsService, RedisService
from models import UserRestrictions


# Configure the database
SQLITE_ASYNC_DATABASE_URL = "sqlite+aiosqlite:///./deployment/db/app.db"
async_engine = create_async_engine(SQLITE_ASYNC_DATABASE_URL, echo=True)
AsyncSessionLocal = sessionmaker(
    async_engine, expire_on_commit=False, class_=AsyncSession
)


# Configure dependency injection.
async def get_db_session():
    """
    At the start of the request we yield the db_session.
    Once the request completes we finally close our session out.
    """
    db = AsyncSessionLocal()
    try:
        yield db
    finally:
        await db.close()


def get_auth_header(header : Optional[str] = Header(None)) -> AuthToken:
    """ Auth headers depend on having a valid header. """
    return AuthToken(header)


def get_user_restrictions(auth: AuthToken = Depends(get_auth_header)) -> UserRestrictions:
    """ User restrictions depend on having a valid auth header. """
    return auth.to_user_restrictions()


def get_metrics_service(
    db: AsyncSession = Depends(get_db_session),
    user_restrictions: UserRestrictions = Depends(get_user_restrictions)
) -> MetricsService:
    """
    Anything that uses this service will require a valid user restrictions and a connection to the
    database.
    """
    dal = MetricsDAL(db, user_restrictions)
    return MetricsService(dal)

def get_redis_service() -> RedisService:
    dal = RedisDAL()
    return RedisService(dal)
