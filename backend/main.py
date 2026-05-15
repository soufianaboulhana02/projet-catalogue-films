from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import httpx
import redis
import json
import os
import models, schemas
from database import engine, SessionLocal

# Création des tables dans la base de données
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Catalogue de Films API")

REDIS_HOST = os.getenv("REDIS_HOST", "redis-service")
cache = redis.Redis(host=REDIS_HOST, port=6379, db=0, decode_responses=True)

@app.get("/")
def read_root():
    return {"message": "API Catalogue Films avec Cache Redis"}

# Configuration du CORS (Autorise Vue.js à parler à FastAPI)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080",
                    "http://127.0.0.1:8080"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Fonction pour obtenir une session de base de données
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- ROUTES TMDB ---

# REMPLACE ICI PAR TA VRAIE CLÉ API (celle qui commence par 1c90...)
TMDB_API_KEY = "1c9021903828653d94a867a5af5db8da" 

@app.get("/movies/popular")
async def get_popular_movies():
    url = f"https://api.themoviedb.org/3/movie/popular?language=fr-FR&page=1&api_key={TMDB_API_KEY}"
    headers = {"accept": "application/json"}
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        if response.status_code != 200:
            raise HTTPException(status_code=502, detail="Erreur avec TMDB")
        return response.json()

@app.get("/movies/search")
async def search_movies(query: str):
    if not query or query.strip() == "":
        raise HTTPException(status_code=400, detail="La recherche ne peut pas être vide.")
        
    url = f"https://api.themoviedb.org/3/search/movie?query={query}&language=fr-FR&api_key={TMDB_API_KEY}"
    headers = {"accept": "application/json"}
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        if response.status_code != 200:
            raise HTTPException(status_code=502, detail="Erreur de communication avec TMDB")
        return response.json()

# --- ROUTES BASE DE DONNÉES (POSTGRESQL) ---

@app.post("/favorites", response_model=schemas.FavoriteResponse)
def add_favorite(movie: schemas.FavoriteCreate, db: Session = Depends(get_db)):
    db_movie = db.query(models.FavoriteMovie).filter(models.FavoriteMovie.tmdb_id == movie.tmdb_id).first()
    if db_movie:
        raise HTTPException(status_code=400, detail="Film déjà dans les favoris")
    
    new_favorite = models.FavoriteMovie(
        tmdb_id=movie.tmdb_id,
        title=movie.title,
        poster_path=movie.poster_path
    )
    db.add(new_favorite)
    db.commit()
    db.refresh(new_favorite)
    return new_favorite

@app.get("/favorites", response_model=list[schemas.FavoriteResponse])
def get_favorites(db: Session = Depends(get_db)):
    return db.query(models.FavoriteMovie).all()

# --- ROUTE DE CACHE (redis) ---

@app.get("/movies/{title}")
def get_movie(title: str):
    # 1. On regarde dans le cache (la RAM, très rapide)
    try:
        cached_movie = cache.get(title)
        if cached_movie:
            print(f"DEBUG: {title} trouvé dans le cache !")
            return json.loads(cached_movie)
    except Exception as e:
        print(f"Erreur Redis: {e}") # Sécurité si Redis est temporairement éteint

    # 2. Si pas en cache, on simule la recherche en DB (ou API externe)
    # C'est ici que tu mettrais ta requête SQL actuelle
    movie_data = {"title": title, "status": "récupéré depuis la base de données"} 
    
    # 3. On enregistre dans Redis pour 1 heure (3600 secondes)
    try:
        cache.setex(title, 3600, json.dumps(movie_data))
    except Exception as e:
        print(f"Erreur d'écriture Redis: {e}")

    return movie_data

# --- AJOUTER UN FAVORI ---
@app.post("/favorites/{user_id}/{movie_title}")
def add_favorite(user_id: str, movie_title: str):
    # On utilise un 'Set' Redis (SADD) pour éviter les doublons automatiquement
    key = f"fav:{user_id}"
    cache.sadd(key, movie_title)
    return {"message": f"{movie_title} ajouté aux favoris"}

# --- RÉCUPÉRER LES FAVORIS ---
@app.get("/favorites/{user_id}")
def get_favorites(user_id: str):
    key = f"fav:{user_id}"
    
    # 1. On récupère tous les éléments du Set dans Redis
    fav_titles = cache.smembers(key)
    
    if not fav_titles:
        # Si rien dans Redis, on pourrait chercher en BDD PostgreSQL ici
        return {"favorites": [], "source": "empty"}

    # 2. On retourne la liste des titres
    return {
        "user_id": user_id,
        "favorites": list(fav_titles),
        "source": "Redis"
    }
