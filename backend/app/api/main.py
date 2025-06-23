from fastapi import APIRouter

from app.api.routes import (
    utils, 
    users, 
    login, 
    projects, 
    news, 
    resource_links, 
    contact, 
    blog,
    suggestions,
    hero,
    about
)
from app.api.routes import home
from app.core.config import settings

api_router = APIRouter()

@api_router.get("/health", status_code=200)
async def health_check():
    """
    Health check endpoint.
    """
    return {"status": "ok"}

api_router.include_router(utils.router, tags=["utils"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(login.router, tags=["login"])
api_router.include_router(projects.router, prefix="/projects", tags=["projects"])
api_router.include_router(news.router, prefix="/news", tags=["news"])
api_router.include_router(resource_links.router, prefix="/resource-links", tags=["resource_links"])
api_router.include_router(contact.router, prefix="/contact", tags=["contact"])
api_router.include_router(blog.router, prefix="/blog", tags=["blog"])
api_router.include_router(suggestions.router, prefix="/suggestions", tags=["suggestions"])
api_router.include_router(hero.router, prefix="/hero", tags=["hero"])
api_router.include_router(about.router, prefix="/about", tags=["about"])
api_router.include_router(home.router)


if settings.ENVIRONMENT == "local":
    pass
