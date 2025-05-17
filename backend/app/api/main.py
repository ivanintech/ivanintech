from fastapi import APIRouter

from app.api.routes import login, utils
from app.api.routes import portfolio
from app.api.routes import blog
from app.api.routes import news
from app.api.routes import contact
from app.core.config import settings

api_router = APIRouter()
api_router.include_router(login.router)
api_router.include_router(utils.router)
api_router.include_router(portfolio.router, prefix="/portfolio", tags=["portfolio"])
api_router.include_router(blog.router, prefix="/content", tags=["content"])
api_router.include_router(news.router, prefix="/news", tags=["content"])
api_router.include_router(contact.router, prefix="/contact", tags=["contact"])


if settings.ENVIRONMENT == "local":
    pass
