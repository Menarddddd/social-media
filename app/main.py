from fastapi import FastAPI
from contextlib import asynccontextmanager

from app import models
from app.core.database import engine, Base
from app.routers.user import router as user_router
from app.routers.post import router as post_router
from app.routers.comment import router as comment_router
from app.exceptions.handler import register_exception_handlers


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

        yield

        await engine.dispose()


app = FastAPI(lifespan=lifespan)

app.include_router(user_router, prefix="/api/users", tags=["users"])
app.include_router(post_router, prefix="/api/posts", tags=["posts"])
app.include_router(comment_router, prefix="/api/comments", tags=["comments"])

register_exception_handlers(app)
