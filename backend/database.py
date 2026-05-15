import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

# Création du moteur de connexion vers PostgreSQL
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Création d'une session pour discuter avec la base
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Classe de base pour créer nos futures tables
Base = declarative_base()

# Fonction pour obtenir une session de base de données dans nos routes FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
