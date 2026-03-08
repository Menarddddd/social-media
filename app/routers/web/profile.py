import shutil
import uuid
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, UploadFile, status, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.templates import templates
from app.core.web_dep import require_user_web
from app.exceptions.exception import DuplicateEntryException
from app.models.user import User
from app.schemas.user import UserUpdate
from app.services.user import my_profile_service, update_profile_service

router = APIRouter()

MEDIA_ROOT = Path("app/media")
PROFILE_PICS_DIR = MEDIA_ROOT / "profile_pics"
PROFILE_PICS_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_CONTENT_TYPES: dict[str, str] = {
    "image/png": ".png",
    "image/jpeg": ".jpg",
    "image/webp": ".webp",
}


@router.post("/profile")
async def profile_update(
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_user_web)],
    first_name: Annotated[str, Form(...)],
    last_name: Annotated[str, Form(...)],
    username: Annotated[str, Form(...)],
    email: Annotated[str, Form(...)],
):
    form_data = UserUpdate(
        first_name=first_name,
        last_name=last_name,
        username=username,
        email=email,
    )

    try:
        await update_profile_service(form_data, db, current_user)
    except DuplicateEntryException:
        return RedirectResponse(
            url="/profile?error=Username%20or%20email%20already%20exists",
            status_code=status.HTTP_303_SEE_OTHER,
        )

    return RedirectResponse(url="/profile", status_code=status.HTTP_303_SEE_OTHER)


@router.get("/profile", response_class=HTMLResponse)
async def profile_page(
    request: Request,
    current_user: Annotated[User, Depends(require_user_web)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    assert current_user.id is not None
    user = await my_profile_service(current_user.id, db)
    if user is None:
        return RedirectResponse("/signin", status_code=status.HTTP_303_SEE_OTHER)

    error = request.query_params.get("error")
    return templates.TemplateResponse(
        "pages/profile.html",
        {"request": request, "user": user, "error": error},
    )


@router.post("/profile/photo")
async def update_profile_photo(
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(require_user_web)],
    photo: Annotated[UploadFile, File(...)],
):
    content_type = photo.content_type or ""
    ext = ALLOWED_CONTENT_TYPES.get(content_type)
    if ext is None:
        return RedirectResponse(
            url="/profile?error=Invalid%20image%20type",
            status_code=status.HTTP_303_SEE_OTHER,
        )

    # delete old pic (optional)
    if user.image_file and user.image_file.startswith("profile_pics/"):
        old_path = MEDIA_ROOT / user.image_file
        if old_path.exists():
            try:
                old_path.unlink()
            except OSError:
                pass

    filename = f"{uuid.uuid4().hex}{ext}"
    dest = PROFILE_PICS_DIR / filename

    with dest.open("wb") as f:
        shutil.copyfileobj(photo.file, f)

    # relative path used by url_for('media', path=...)
    user.image_file = f"profile_pics/{filename}"

    await db.flush()
    await photo.close()

    return RedirectResponse(url="/profile", status_code=status.HTTP_303_SEE_OTHER)
