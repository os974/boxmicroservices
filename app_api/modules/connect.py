"""Configuration de la connexion base de données (SQLAlchemy).

Pourquoi ce module existe à part : centraliser la résolution de l'URL de
connexion et l'instanciation de l'`engine` à un seul endroit, pour que les
tests, le runtime Docker Compose et un éventuel run local utilisent
exactement le même point d'entrée.

Résolution de `DATABASE_URL` par priorité (voir bloc ci-dessous) :

1. Variable d'env `DATABASE_URL` brute → c'est par ce canal que `conftest.py`
   injecte un SQLite de test *avant* d'importer ce module. Indispensable pour
   ne pas avoir besoin d'un Postgres pendant `pytest`.
2. Construction depuis `POSTGRES_*` → chemin emprunté en Docker Compose, où
   `POSTGRES_HOST=db` est fixé par le `docker-compose.yml` (résolution DNS du
   réseau Compose, pas `localhost`).
3. Fallback SQLite local → permet un `uv run uvicorn ...` à froid sans `.env`.
   ATTENTION : compromis pédagogique assumé — on ne *fail-fast* pas si les
   vars Postgres manquent, on retombe en SQLite silencieusement. À renforcer
   pour un usage prod (cf. RETEX.md).
"""

import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# load_dotenv() doit tourner AVANT tout os.getenv ci-dessous : sinon les vars
# du fichier .env ne sont pas peuplées au moment de la lecture.
load_dotenv()

# Priorité 1 : DATABASE_URL brute (utilisée par les tests pour pointer SQLite).
DATABASE_URL = os.getenv("DATABASE_URL")

# Priorité 2 : reconstruire l'URL Postgres depuis les vars POSTGRES_*.
# Sépare host/port/user pour rester compatible avec la convention officielle
# de l'image postgres:15 (qui lit ces mêmes vars côté serveur).
if not DATABASE_URL:
    DB_USER = os.getenv("POSTGRES_USER")
    DB_PASSWORD = os.getenv("POSTGRES_PASSWORD")
    DB_NAME = os.getenv("POSTGRES_DB")
    DB_PORT = os.getenv("POSTGRES_PORT", "5432")
    DB_HOST = os.getenv("POSTGRES_HOST", "localhost")

    if DB_USER and DB_NAME:
        DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    else:
        # Priorité 3 : fallback SQLite. Voir docstring du module.
        DATABASE_URL = "sqlite:///./app_api/data/testsqlite.db"

# `check_same_thread=False` n'est valide *que* pour SQLite : par défaut SQLite
# interdit le partage de connexion entre threads, ce qui casse FastAPI qui
# sert chaque requête potentiellement dans un thread différent. Postgres n'a
# pas cette contrainte → on n'ajoute l'arg que si on est en SQLite.
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)

# `autocommit=False` + `autoflush=False` : on veut un contrôle explicite des
# transactions (commit/rollback à la main dans les CRUD), pas de magie qui
# pousse les changements en BDD au mauvais moment.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base declarative partagée : tous les modèles (cf. models/models.py) doivent
# en hériter pour être enregistrés dans le même `Base.metadata` et donc créés
# par `Base.metadata.create_all(bind=engine)` au démarrage de l'API.
Base = declarative_base()


def get_db():
    """Fournir une session de BDD à FastAPI via `Depends(get_db)`.

    Pourquoi un générateur et pas une simple fonction : FastAPI traite
    `yield` comme une dépendance à teardown — la session est fermée
    automatiquement après la requête, même en cas d'exception. C'est le
    pattern recommandé pour éviter les fuites de connexion.

    Yields:
        Session: session SQLAlchemy fraîche, scoppée à la requête HTTP.

    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
