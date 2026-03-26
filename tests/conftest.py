import os
import pathlib
import sys

# Ajouter la racine du projet au sys.path
sys.path.append(str(pathlib.Path(__file__).resolve().parent.parent))

# Forcer SQLite pendant les tests AVANT d'importer app_api.modules.connect
os.environ["DATABASE_URL"] = "sqlite:///./tests/test_db.sqlite"

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app_api.modules.connect import Base

# On recrée un engine de test pour SQLite
engine = create_engine(
    "sqlite:///./tests/test_db.sqlite", connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session", autouse=True)
def setup_db():
    """Crée les tables au début de la session de test et les supprime à la fin."""
    Base.metadata.create_all(bind=engine)
    yield
    # Optionnel : décommenter pour supprimer la base après les tests
    # Base.metadata.drop_all(bind=engine)
    # if os.path.exists("./tests/test_db.sqlite"):
    #     os.remove("./tests/test_db.sqlite")

@pytest.fixture
def db_session():
    """Fournit une session de base de données propre pour chaque test."""
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()
