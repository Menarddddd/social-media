from fastapi import APIRouter, status
from fastapi.responses import RedirectResponse


router = APIRouter()


@router.post("/logout")
async def logout():
    resp = RedirectResponse(url="/signin", status_code=status.HTTP_303_SEE_OTHER)
    resp.delete_cookie("access_token", path="/")

    return resp
