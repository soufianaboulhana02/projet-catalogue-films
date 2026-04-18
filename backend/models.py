from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from database import Base

class FavoriteMovie(Base):
    __tablename__ = "favorite_movies"

    id = Column(Integer, primary_key=True, index=True)
    tmdb_id = Column(Integer, unique=True, index=True) # L'ID officiel du film sur TMDB
    title = Column(String, index=True)
    poster_path = Column(String) # Le lien vers l'affiche du film
    added_at = Column(DateTime(timezone=True), server_default=func.now()) # Date d'ajout automatique
