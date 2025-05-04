# Import specific CRUD functions or the modules themselves

# Option 1: Import modules (allows crud.contact.create_contact_message)
from . import crud_contact as contact
from . import crud_portfolio as portfolio
from . import crud_blog as blog
from . import crud_news as news
# Import user and item crud if/when they exist
# from . import crud_user as user
# from . import crud_item as item

# Option 2: Import specific functions (would require changing calls in routes)
# from .crud_project import get_projects
# from .crud_blog import get_blog_posts, get_blog_post_by_slug
# from .crud_news import get_news_items
# from .crud_contact import create_contact_message

# Podrías añadir aquí importaciones para create/update/delete si las implementas 