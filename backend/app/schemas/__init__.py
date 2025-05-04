# app/schemas/__init__.py
# Dejar vacío o añadir imports si es necesario más adelante 
from .project import ProjectRead
from .blog import BlogPostRead
from .news import NewsItemRead
from .contact import ContactForm
from .token import Token, TokenPayload
from .user import User, UserCreate, UserUpdate, NewPassword
from .msg import Message 