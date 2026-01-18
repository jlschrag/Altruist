from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from api import router
from config import async_engine
from models import Base, AuthException

"""
This is the main entry point for the application.
Adding this to the __init__.py file allows us to run the application using the command:
    python -m uvicorn --app-dir src/app __init__:app --lifespan on

In terms of clean arch, this is in the application layer.
"""


async def init_db() -> None:
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Things to do on startup.
    await init_db()
    yield
    # Things to do on shutdown.
    ...

app = FastAPI(lifespan=lifespan)
app.include_router(router)

@app.exception_handler(AuthException)
async def auth_exception_handler(request: Request, exc: AuthException):
    return JSONResponse(
        status_code=400,
        content={"message": exc.message},
    )