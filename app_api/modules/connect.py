"""Database connection configuration using SQLAlchemy.

This module initializes the database engine and session used by the API.
The application uses a local SQLite database stored in app_api/data/.
"""

import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Charger les variables d'environnement
load_dotenv()

# On vérifie d'abord si DATABASE_URL est déjà dans l'environnement (ex: par les tests)
DATABASE_URL = os.getenv("DATABASE_URL")

# Si non, on tente de construire l'URL PostgreSQL à partir du .env
if not DATABASE_URL:
    DB_USER = os.getenv("POSTGRES_USER")
    DB_PASSWORD = os.getenv("POSTGRES_PASSWORD")
    DB_NAME = os.getenv("POSTGRES_DB")
    DB_PORT = os.getenv("POSTGRES_PORT", "5432")
    DB_HOST = os.getenv("POSTGRES_HOST", "localhost")

    if DB_USER and DB_NAME:
        DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    else:
        # Fallback de secours ultime
        DATABASE_URL = "sqlite:///./app_api/data/testsqlite.db"

# Création de l'engine
# On ajoute check_same_thread uniquement pour SQLite
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)

# Session locale pour les transactions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base pour la définition des modèles
Base = declarative_base()


def get_db():
    """Dependency function to provide a database session.

    Yields:
        Session: SQLAlchemy session

    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
