from app.crud.base import CRUDBase
from app.db.models.hero_media import HeroMedia
from app.schemas.hero_media import HeroMediaCreate, HeroMediaUpdate

class CRUDHeroMedia(CRUDBase[HeroMedia, HeroMediaCreate, HeroMediaUpdate]):
    pass

hero_media = CRUDHeroMedia(HeroMedia) 