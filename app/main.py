from fastapi import FastAPI
from contextlib import asynccontextmanager

from app import models  # this loads the models
from app.core.database import engine, Base
from app.config.load_main import (
    register_routers,
    register_exception_handlers,
    mount_folders,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

        yield

        await engine.dispose()


app = FastAPI(lifespan=lifespan)

mount_folders(app)
register_routers(app)
register_exception_handlers(app)
