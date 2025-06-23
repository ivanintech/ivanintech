from app.crud.base import CRUDBase
from app.db.models.about_media import AboutMedia
from app.schemas.about_media import AboutMediaCreate, AboutMediaUpdate

class CRUDAboutMedia(CRUDBase[AboutMedia, AboutMediaCreate, AboutMediaUpdate]):
    pass

about_media = CRUDAboutMedia(AboutMedia) 