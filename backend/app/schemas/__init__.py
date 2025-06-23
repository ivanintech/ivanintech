# app/schemas/__init__.py
# Dejar vacío o añadir imports si es necesario más adelante 
from .project import ProjectRead
from .blog import BlogPostRead
from .news import NewsItemRead
from .contact import ContactForm
from .token import Token, TokenPayload
from .user import User, UserCreate, UserUpdate, NewPassword, UserWithAvatar
from .msg import Message
from .hero_media import HeroMedia, HeroMediaCreate, HeroMediaUpdate
from .blog_suggestion import BlogSuggestionRead, BlogSuggestionCreate, BlogSuggestionUpdate
from .about_media import AboutMedia, AboutMediaCreate, AboutMediaUpdate 