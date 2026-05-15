from pydantic import BaseModel
from datetime import datetime
from typing import Optional

# Les données requises pour AJOUTER un favori
class FavoriteCreate(BaseModel):
    tmdb_id: int
    title: str
    poster_path: Optional[str] = None

# Les données RENVOYÉES par l'API quand on consulte les favoris
class FavoriteResponse(FavoriteCreate):
    id: int
    added_at: datetime

    class Config:
        from_attributes = True # Permet à Pydantic de lire les données de SQLAlchemy
