from typing import Annotated
from fastapi import APIRouter, Depends, Request, Query
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.templates import templates
from app.core.web_dep import require_user_web
from app.models.user import User
from app.services.post import feed_post_service_web

router = APIRouter()
from typing import Annotated
from fastapi import Query
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession


@router.get("/feed", response_class=HTMLResponse)
async def feed_page(
    request: Request,
    user: Annotated[User, Depends(require_user_web)],
    db: Annotated[AsyncSession, Depends(get_db)],
    page: Annotated[int, Query(ge=1)] = 1,
    limit: Annotated[int, Query(ge=1, le=50)] = 20,
):
    feed_posts, pages = await feed_post_service_web(db, page, limit)

    return templates.TemplateResponse(
        "pages/feed.html",
        {
            "request": request,
            "user": user,
            "feed_posts": feed_posts,
            "page": page,
            "pages": pages,
            "limit": limit,
        },
    )
