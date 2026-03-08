from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.exceptions.exception import (
    DuplicateEntryException,
    FieldNotFoundException,
    InvalidCredentialsError,
)
from app.exceptions.handler import (
    duplicate_entry_exception_handler,
    field_not_found_exception_handler,
    invalid_credentials_error_handler,
)
from app.routers.api.user import router as user_router
from app.routers.api.post import router as post_router
from app.routers.api.comment import router as comment_router

from app.routers.web.exceptions import starlette_http_exception_handler
from app.routers.web.signup import router as signup_router
from app.routers.web.signin import router as signin_router
from app.routers.web.feed import router as feed_router
from app.routers.web.profile import router as profile_router
from app.routers.web.logout import router as logout_router
from app.routers.web.comment import router as comment_web_router
from app.routers.web.user import router as user_web_router
from app.routers.web.post_action import router as post_action_router
from app.routers.web.post import router as post_web_reouter


def register_routers(app: FastAPI):
    # API
    app.include_router(user_router, prefix="/api/users", tags=["users"])
    app.include_router(post_router, prefix="/api/posts", tags=["posts"])
    app.include_router(comment_router, prefix="/api/comments", tags=["comments"])

    # WEB
    app.include_router(signup_router, include_in_schema=False)
    app.include_router(signin_router, include_in_schema=False)
    app.include_router(feed_router, include_in_schema=False)
    app.include_router(profile_router, include_in_schema=False)
    app.include_router(logout_router, include_in_schema=False)
    app.include_router(comment_web_router, include_in_schema=False)
    app.include_router(user_web_router, include_in_schema=False)
    app.include_router(post_action_router, include_in_schema=False)
    app.include_router(post_web_reouter, include_in_schema=False)


def register_exception_handlers(app: FastAPI):
    app.add_exception_handler(FieldNotFoundException, field_not_found_exception_handler)
    app.add_exception_handler(
        DuplicateEntryException, duplicate_entry_exception_handler
    )
    app.add_exception_handler(
        InvalidCredentialsError, invalid_credentials_error_handler
    )
    app.add_exception_handler(StarletteHTTPException, starlette_http_exception_handler)


def mount_folders(app: FastAPI):
    app.mount("/static", StaticFiles(directory="app/static"), name="static")
    app.mount("/media", StaticFiles(directory="app/media"), name="media")
