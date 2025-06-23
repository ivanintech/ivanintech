from app.crud.base import CRUDBase
from app.db.models.blog_suggestion import BlogSuggestion
from app.schemas.blog_suggestion import BlogSuggestionCreate, BlogSuggestionUpdate

class CRUDBlogSuggestion(CRUDBase[BlogSuggestion, BlogSuggestionCreate, BlogSuggestionUpdate]):
    pass

blog_suggestion = CRUDBlogSuggestion(BlogSuggestion) 