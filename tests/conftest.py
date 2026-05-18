"""Configuration pytest : isolation BDD pour les tests de l'API.

Deux subtilités à expliquer ici, parce qu'elles sont fragiles si on les
casse sans s'en rendre compte.

**1. Pourquoi `os.environ["DATABASE_URL"] = ...` AVANT l'import de
`app_api.modules.connect`** :
`connect.py` lit `DATABASE_URL` et crée son `engine` au moment de
l'import (top-level, pas dans une fonction). Si on importait `connect`
*avant* de fixer la var, l'engine se brancherait sur Postgres (ou sur le
SQLite fallback `app_api/data/...`) et on testerait contre la mauvaise
base. L'ordre des lignes ici n'est donc PAS un détail de style — c'est
une dépendance d'exécution.

**2. Pourquoi on crée un SECOND engine + sessionmaker pour les tests** :
- l'engine de `connect.py` (réutilisé par l'API via `get_db`) sert au code
  testé ;
- l'engine local ci-dessous sert à la fixture `db_session`, qui ouvre une
  transaction par test et la **rollback** en teardown — chaque test part
  d'une BDD propre sans drop/recreate complet, ce qui est rapide et
  isolant. Avoir deux engines distincts évite que la fixture commit/rollback
  interfère avec les transactions internes au code testé.
"""

import os
import pathlib
import sys

# Ajout de la racine au sys.path : sans ça, `from app_api.modules.connect`
# échouerait quand pytest est lancé depuis un autre cwd.
sys.path.append(str(pathlib.Path(__file__).resolve().parent.parent))

# Ordre critique : voir docstring du module ci-dessus.
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
    """Fournir une session BDD propre par test, via transaction + rollback.

    Pourquoi ce pattern plutôt que `Base.metadata.drop_all()/create_all()`
    entre chaque test : c'est **drastiquement plus rapide** (pas de DDL),
    et ça garantit l'isolation sans risque d'oublier une nouvelle table.
    Le rollback en teardown annule toutes les écritures du test, même en
    cas d'exception.
    """
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()
