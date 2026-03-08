from fastapi.templating import Jinja2Templates
from zoneinfo import ZoneInfo

templates = Jinja2Templates(directory="app/templates")

APP_TZ = ZoneInfo("Asia/Manila")  # change to your timezone


def dt(value):
    if value is None:
        return ""
    return value.astimezone(APP_TZ).strftime("%b %d, %Y %I:%M %p")


templates.env.filters["dt"] = dt
