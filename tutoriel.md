# tutoriel projet2 orchestration #

ATTENTION : suite a des probleme de version avec python 3.13 j ai du passer en cours de developpement en python 3.11

## phase A ##
### Étape 1 — Vérifier la structure du projet ###
#### Créer la structure suivante dans app_api : ####
```
.
├── app_api
│   ├── main.py
│   ├── pyproject.toml
│   ├── maths
│   │   ├── __init__.py
│   │   └── mon_module.py
│   ├── modules
│   │   ├── __init__.py
│   │   ├── connect.py
│   │   └── crud.py
│   ├── models
│   │   ├── __init__.py
│   │   └── models.py
│   └── data
│       └── moncsv.csv
│
├── app_front
│   ├── main.py
│   ├── pages
│   │   ├── 0_insert.py
│   │   └── 1_read.py
│   ├── pyproject.toml
│   └── Dockerfile
│
├── tests
│   └── test_math_csv.py
│   ├── test_api.py
```
et j ai supprimé "test_main.py" du dossier "tests"

### Étape 2 — Implémenter la base SQLite avec SQLAlchemy ###

1) Créer la connexion dans app_api/modules/connect.py.

Responsabilités :
- créer l’engine SQLAlchemy
- créer la session
- créer la base SQLite locale
- 
```
"""
"""
Database connection configuration using SQLAlchemy.

This module initializes the database engine and session used by the API.
The application uses a local SQLite database stored in app_api/data/.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Définir le chemin du fichier SQLite
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "data", "testsqlite.db")
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

# URL de connexion SQLAlchemy pour SQLite
SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH}"

# Création de l'engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}  # requis pour SQLite et threads multiples
)

# Session locale pour les transactions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base pour la définition des modèles
Base = declarative_base()


def get_db():
    """
    Dependency function to provide a database session.

    Yields:
        Session: SQLAlchemy session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```
2) Créer le modèle SQLAlchemy
   
Dans app_api/models/models.py :

```
"""
ORM models for the application.

Defines the Operation table to store mathematical operations.
"""

from sqlalchemy import Column, Integer, String, Float
from ..modules.connect import Base  # importer Base depuis connect, pas depuis lui-même

class Operation(Base):
    """
    SQLAlchemy ORM model for a mathematical operation.

    Attributes:
        id (int): Primary key.
        operation (str): Operation type ("add", "sub", "square").
        a (float): First operand.
        b (float | None): Second operand (optional for square).
    """
    __tablename__ = "operations"
    __table_args__ = {"extend_existing": True}  # Evite l'erreur "table already defined"

    id = Column(Integer, primary_key=True, index=True)
    operation = Column(String, nullable=False)
    a = Column(Float, nullable=False)
    b = Column(Float, nullable=True)
```

3) Implémenter les opérations CRUD

Dans app_api/modules/crud.py :

```
"""
CRUD operations for the Operation model.

Provides functions to insert and retrieve operations from the database.
"""

from sqlalchemy.orm import Session
from app_api.models.models import Operation

def create_data(db: Session, operation: str, a: float, b: float | None = None) -> Operation:
    """
    Insert a new operation into the database.

    Args:
        db (Session): Database session
        operation (str): Operation type ("add", "sub", "square")
        a (float): First operand
        b (float | None): Second operand (optional)

    Returns:
        Operation: The newly created Operation object
    """
    db_operation = Operation(operation=operation, a=a, b=b)
    db.add(db_operation)
    db.commit()
    db.refresh(db_operation)
    return db_operation

def get_all_data(db: Session) -> list[Operation]:
    """
    Retrieve all operations from the database.

    Args:
        db (Session): Database session

    Returns:
        list[Operation]: List of Operation objects
    """
    return db.query(Operation).all()
```

4) fichier pyproject.toml dans app_api

supprimer "pyproject.toml" ainsi que le dossier  ".venv" a la racine de mon projet  

creer le fichier "pyproject.toml"  dans le dossier "app_api"

deacitivate mo ancien environnement "venv"
et activer le nouveau environnement 
```
.venv\Scripts\activate
```

```
cd app_api
uv init
uv add fastapi
uv add uvicorn
uv add sqlalchemy
uv add pydantic
uv add pytest --dev
uv add pytest-cov --dev
```
```
uv sync
```

Ajouter la config pytest demandée par le projet dans app_api/pyproject.toml
```
[tool.pytest.ini_options]
pythonpath = ["."]
testpaths = ["tests"]
```

Vérifier que tout fonctionne
```
uv run python -c "import fastapi, sqlalchemy"
```

5) brancher l’API FastAPI avec la base de données et le CRUD

dans app_api/main.py :

```
"""
FastAPI application entry point.

Provides API endpoints to insert and list mathematical operations.
"""

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from app_api.modules.connect import Base, engine, get_db
from app_api.modules.crud import create_data, get_all_data
from .models.models import Operation

# Crée les tables SQLite si elles n'existent pas
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Operations API", description="API for managing operations in SQLite database", version="1.0.0")

@app.get("/")
def read_root():
    """
    Root endpoint.

    Returns a simple message to indicate that the API is running.

    Returns:
        dict: A dictionary with a message.
    """
    return {"message": "API is running"}


@app.post("/operations/")
def add_operation(operation: str, a: float, b: float | None = None, db: Session = Depends(get_db)):
    """
    Add a new mathematical operation.

    Args:
        operation (str): Operation type ("add", "sub", "square")
        a (float): First operand
        b (float | None): Second operand (optional)
        db (Session): Database session (dependency)

    Returns:
        dict: Created operation info
    """
    return create_data(db, operation, a, b).__dict__

@app.get("/operations/")
def list_operations(db: Session = Depends(get_db)):
    """
    List all operations stored in the database.

    Args:
        db (Session): Database session (dependency)

    Returns:
        list[dict]: List of operations as dictionaries
    """
    operations = get_all_data(db)
    return [op.__dict__ for op in operations]
```

# création automatique des tables
Base.metadata.create_all(bind=engine)

```
@app.get("/")
def root():
    """
    Health check endpoint.
    """
    return {"message": "API is running"}


@app.post("/data")
def add_data(value_a: float, value_b: float, result: float, db: Session = Depends(get_db)):
    """
    Insert a new record into the database.
    """
    return create_data(db, value_a, value_b, result)


@app.get("/data")
def read_data(db: Session = Depends(get_db)):
    """
    Retrieve all stored records.
    """
    return get_all_data(db)
```

6) Test
   
A la racine du projet:

```
uv run uvicorn app_api.main:app --reload
```
Ouvrir dans le navigateur :
http://127.0.0.1:8000/docs

Tester l’insertion et la lecture des données avec les endpoints /data :
```
curl -X POST "http://127.0.0.1:8000/operations/?operation=add&a=10&b=5"
```
```
curl "http://127.0.0.1:8000/data"
```

Vérifier la base SQLite (facultatif) :
```
sqlite3 app_api/test.db "SELECT * FROM data;"
```

### Étape 3 — Implémenter Streamlit ###

1) fichier pyproject.toml dans app_api
```
cd app_front
uv init
uv add streamlit
uv add sqlalchemy requests pandas
```

activer le nouveau environnement 
```
.venv\Scripts\activate
```

Après installation, tu peux vérifier que Streamlit est disponible :

```
uv run streamlit --version
```

Ensuite, pour lancer ton frontend Streamlit :
```
uv run streamlit run main.py
```

2) app_front/main.py

```
"""
Streamlit application entry point.

This module initializes the main interface of the frontend application.
It provides a simple landing page explaining the purpose of the app.

The frontend communicates with the FastAPI backend to:
- Insert new mathematical operations
- Retrieve stored operations from the database
"""

import streamlit as st

st.set_page_config(
    page_title="Math Operations App",
    page_icon="🧮",
    layout="centered",
)

st.title("Math Operations Application")

st.write(
    """
This Streamlit application allows users to interact with a backend API
that stores mathematical operations in a database.

Available features:
- Insert new mathematical operations
- View previously stored operations
"""
)

st.info(
    "Use the navigation menu on the left to insert or view operations."
)

```

3) app_front/pages/0_insert.py

```
"""
Streamlit page used to insert mathematical operations.

This page provides a form allowing the user to create a new
mathematical operation. The operation is sent to the FastAPI backend
via an HTTP POST request.

Supported operations:
- add
- sub
- square

The backend API stores the operation in a SQLite database.
"""

import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000/operations/"

st.title("Insert a Mathematical Operation")

operation = st.selectbox(
    "Select operation",
    ["add", "sub", "square"]
)

a = st.number_input("Value A", value=0.0)

b = None
if operation != "square":
    b = st.number_input("Value B", value=0.0)

if st.button("Submit operation"):
    params = {
        "operation": operation,
        "a": a,
        "b": b,
    }

    try:
        response = requests.post(API_URL, params=params)

        if response.status_code == 200:
            st.success("Operation successfully stored.")
            st.json(response.json())
        else:
            st.error("Error while inserting operation.")

    except requests.exceptions.ConnectionError:
        st.error("Unable to connect to the API. Make sure FastAPI is running.")
```

4) app_front/pages/1_read.py

```
"""
Streamlit page used to display stored operations.

This page retrieves all mathematical operations stored in the
database by calling the FastAPI backend API.

The retrieved data is displayed in a tabular format using
a pandas DataFrame.
"""

import streamlit as st
import requests
import pandas as pd

API_URL = "http://127.0.0.1:8000/operations/"

st.title("Stored Mathematical Operations")

if st.button("Load operations"):
    try:
        response = requests.get(API_URL)

        if response.status_code == 200:
            data = response.json()

            if len(data) == 0:
                st.warning("No operations found in the database.")
            else:
                df = pd.DataFrame(data)
                st.dataframe(df)

        else:
            st.error("Error while retrieving operations.")

    except requests.exceptions.ConnectionError:
        st.error("Unable to connect to the API. Make sure FastAPI is running.")


```
5) pour tester
- Terminal 1 — API
Depuis la racine du projet :
```
cd app_api
.venv\Scripts\activate
cd..

uv run uvicorn app_api.main:app --reload
```

API disponible sur :

http://127.0.0.1:8000
http://127.0.0.1:8000/docs

- Terminal 2 — Frontend
```
cd app_front
.venv\Scripts\activate
uv run streamlit run main.py
```

Interface :

http://localhost:8501

- modification de fichier pour interger resultat
=> suppression de testSquilte.db 
=> recrer le fichier testSquilte.db:

```
cd app_api
uv add pandas
uv sync
.venv\Scripts\activate   # activer ton environnement
uv run uvicorn main:app --reload
```

```
curl -X POST "http://127.0.0.1:8000/operations/?operation=add&a=10&b=5" -H "accept: application/json"
curl -X POST "http://127.0.0.1:8000/operations/?operation=square&a=7" -H "accept: application/json"
curl -X GET "http://127.0.0.1:8000/operations/" -H "accept: application/json"
curl -X PUT "http://127.0.0.1:8000/operations/1?operation=sub&a=20&b=3" -H "accept: application/json"
curl -X DELETE "http://127.0.0.1:8000/operations/1" -H "accept: application/json"
```

### Étape 4 — Validez votre API avec Pytest (maths et api) ###

- creation du fichier test_api.py
- suppression de test_main.py
- modification de test_math_csv.py

pour lancer les tests :
```
uv run pytest
```
ou 

```
uv run --project app_api pytest --cov=app_api tests/
```

------
Note personnel :

Probleme quand on push le projet sur les repositorie car actions ne peux pas valider car il ne trouve pas de fichier pyproject.toml a la racine du projet comme c etait le cas dans le projet initiale.

Le passage d'une structure monolithique à une architecture "micro-services" (avec app_api et app_front) a brisé votre configuration CI car uv ne trouve plus de fichier pyproject.toml à la racine pour synchroniser l'environnement.

Solution : Utiliser les "Workspaces" de uv (La plus élégante)
  C'est la solution recommandée par uv pour gérer plusieurs projets dans un seul dépôt (monorepo). Elle permet de garder un seul
  environnement virtuel à la racine tout en gérant les dépendances de chaque sous-dossier.

  Actions à réaliser :
   1. Créer un pyproject.toml à la racine pour déclarer le "Workspace" et centraliser les outils de développement (Ruff, Pytest).
   2. Mettre à jour le fichier ci.yml pour qu'il utilise ce nouvel environnement.
        modifier "uv run pytest --cov=. --cov-report=xml" pour mettre a la place "uv run pytest --cov-report=xml"

il y avait des probleme j ai du faire des modifications dans "app_api/pyproject.toml" et "app_front/pyproject.toml"
   1. app_api utilise maintenant pandas < 3, ce qui lui permet de cohabiter avec le Front (Streamlit).
   2. Tous les fichiers (pyproject.toml racine, API et Front) indiquent désormais une plage de version Python 3.11 ou 3.12 (>=3.11, <3.13). Cela empêche uv de bloquer sur des versions futures comme la 3.14.

il y a avait un probleme avec sphinx car on doit ajouter sphinx et le thème furo (utilisiez dans le projet initial) au groupe de dépendances de développement.
sphinx et furo ne sont pas dans votre pyproject.toml. On doit les ajouter maintenant à votre dependency-groups.dev afin que uv puisse les installer automatiquement lors de votre CI

Pour que Sphinx puisse générer la documentation de votre API (en lisant vos fichiers .py), il doit savoir où trouver le code. Dans un Workspace uv, nous avons déjà configuré le pythonpath pour Pytest, mais nous devons nous assurer que votre fichier docs/source/conf.py inclut bien la racine dans son chemin de recherche.
ans votre fichier docs/source/conf.py. Le chemin configuré était sys.path.insert(0, os.path.abspath("../../app")). Or, dans votre nouveau projet, vous n'avez plus de dossier app/ à la racine. Vous avez maintenant app_api/ et app_front/.

------

### Étape 4 — mise ajour de readme et de la documentation sphinx ###

1. Correction de mon_module.rst : Il pointe maintenant vers maths.mon_module.
2. Ajout de api_db.rst et models.rst : Pour documenter vos scripts de base de données et vos modèles.
3. Mise à jour de index.rst : Pour inclure ces nouvelles pages dans le menu.
4. Reconstruction : J'ai utilisé uv run sphinx-build pour générer la doc et je l'ai copiée dans votre dossier public/.

5. Création de app_api/__init__.py pour faire de app_api un package Python valide.
6. Correction de app_api/models/models.py en remplaçant l'import relatif par un import absolu (from app_api.modules.connect import Base).
7. Mise à jour des fichiers .rst (mon_module.rst, api_db.rst, models.rst) pour utiliser les chemins de modules complets (ex: app_api.maths.mon_module).
8. Reconstruction complète de la documentation.

## phase B ##

1. Créer un fichier .env dans la racine du projet (ou dans app_api) pour stocker les paramètres sensibles, par exemple :
```
# .env
API_HOST=127.0.0.1
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=mydb
POSTGRES_PORT=5432
```

2. Créer .env.example (version template à partager sur GitHub) :
```
# .env.example
API_HOST=
POSTGRES_USER=
POSTGRES_PASSWORD=
POSTGRES_DB=
POSTGRES_PORT=
```
3. Mettre à jour ton code pour utiliser ces variables :
- Dans app_api/modules/connect.py :
```
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

# URL de connexion PostgreSQL (host 'db' pour Docker Compose)
DATABASE_URL = (
    f"postgresql+psycopg2://{os.getenv('POSTGRES_USER')}:"
    f"{os.getenv('POSTGRES_PASSWORD')}@db:{os.getenv('POSTGRES_PORT', 5432)}/"
    f"{os.getenv('POSTGRES_DB')}"
)

# Création de l'engine
engine = create_engine(DATABASE_URL)

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
```

-Mise à jour de main.py : les routes sont passées de /operations/ à /data.
- Frontend (app_front) :
    Mise à jour des pages 0_insert.py et 1_read.py pour utiliser API_HOST et la nouvelle route /data.
- Hygiène : Vérification que .env et .venv sont bien ignorés (je les ai ajoutés au .gitignore et .dockerignore).
- Corrigé la configuration pour que les tests puissent s'exécuter sans erreur.
  Voici le changement stratégique :
   1. Isolation des tests : J'ai mis à jour tests/conftest.py pour qu'il force l'utilisation de sqlite:///./tests/test_db.sqlite avant même d'importer le code de l'API.
   2. Priorité à la configuration de test : J'ai modifié app_api/modules/connect.py pour qu'il vérifie d'abord si une DATABASE_URL est déjà définie (ce que fait conftest.py). Si elle n'est pas définie (cas du lancement normal de l'app), il continue d'utiliser votre configuration PostgreSQL du fichier .env.

## Phase C : Orchestration Docker Compose (test en local) ##
-app_api\main.py
supprimer le préfixe app_api. des imports.
=> remplacer :

```
from app_api.modules.connect import Base, engine get_db
from app_api.modules.crud import (
```
par
```
from modules.connect import Base, engine, get_db
from modules.crud import (
```
idem dans app_api\models\models.py et app_api\modules\crud.py et app_api\main.py

- app_api > Dockerfile

```
# Utilisation d'une image Python légère
FROM python:3.11-slim

# Installation de uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Définition du répertoire de travail
WORKDIR /app

# On s'assure qu'aucun dossier .venv local n'interfère
COPY pyproject.toml ./
RUN uv sync --no-install-project

# On ajoute le dossier .venv/bin au PATH pour pouvoir lancer uvicorn
ENV PATH="/app/.venv/bin:$PATH"

# Copie du reste de l'application
COPY . .

# Exposition du port
EXPOSE 8000

# Lancement de l'API
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]


```

- app_front > Dockerfile
```
# Utilisation d'une image Python légère
FROM python:3.11-slim

# Installation de uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Définition du répertoire de travail
WORKDIR /app

# Préparation de l'environnement virtuel
COPY pyproject.toml ./
RUN uv sync --no-install-project

# On ajoute le dossier .venv/bin au PATH pour pouvoir lancer streamlit
ENV PATH="/app/.venv/bin:$PATH"

# Copie du reste de l'application
COPY . .

# Exposition du port streamlit
EXPOSE 8501

# Lancement de streamlit
CMD ["streamlit", "run", "main.py", "--server.port", "8501", "--server.address", "0.0.0.0"]
```

- Docker-compose.yml

```
services:
  db:
    image: postgres:15
    container_name: postgres-db
    environment:
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: ${POSTGRES_DB}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - api-db

  api:
    build:
      context: ./app_api
    container_name: fastapi-api
    environment:
      - POSTGRES_USER=${POSTGRES_USER}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
      - POSTGRES_DB=${POSTGRES_DB}
      - POSTGRES_PORT=${POSTGRES_PORT:-5432}
      - POSTGRES_HOST=db
      - PYTHONPATH=.
    depends_on:
      - db
    networks:
      - api-db
      - front-api
    ports:
      - "8000:8000"

  front:
    build:
      context: ./app_front
    container_name: streamlit-front
    environment:
      - API_HOST=api
    depends_on:
      - api
    networks:
      - front-api
    ports:
      - "8501:8501"

networks:
  front-api:
  api-db:

volumes:
  postgres_data:

```

pour tester :
- Lancez simplement la commande suivante à la racine :
```
docker-compose up --build
```
Une fois lancé :
   * Frontend : Accédez à http://localhost:8501.
   * API : Accédez à http://localhost:8000/docs.

Commandes pour reconstruire les images proprement :
```
docker-compose down
docker-compose up --build
```
autres commandes :
```
docker-compose down --volumes --remove-orphans
docker-compose build --no-cache
docker-compose up
```
## Phase D: Automatisation et Distribution (GitHub & DockerHub) ##

### CI Améliorée (Gitleaks) ### 

1) créer un nouveau workflow GitHub : ".github/workflows/security.yml"

a noter :
Depuis les versions récentes, GITHUB_TOKEN est obligatoire pour scanner les pull requests.

Il faut simplement ajouter le token dans ton workflow GitHub Actions.

2) Fichier security.yml
```
name: Security Scan

on:
  push:
    branches:
      - main
      - dev
  pull_request:
    branches:
      - main
      - dev

jobs:
  gitleaks:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Run Gitleaks scan
        uses: gitleaks/gitleaks-action@v2
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```
explications :
fetch-depth: 0	=> permet de scanner tout l'historique Git
gitleaks-action	=> lance le scan de secrets

3) test Faites exprès de pousser une variable dans un commit, constatez l'échec de la CI, puis nettoyez votre historique
- ajouter dans README 
  "PASSWORD="<your_password_here>"" et
  "API_KEY=<your_api_key_here>"
- pusher le code :
```
git add .
git commit -m "test secret"
git push
```
- voir l'échec de la CI dans GitHub → Actions
- Security Scan ❌ FAILED
```
git reset --hard HEAD~1
git reset --hard HEAD~1
```

### Livraison Continue (CD) ###

1) integre le security.yml dans ci.yml et supprimer apres security.yml

```
name: CI

permissions:
  contents: write

# Déclenchement sur push ou PR sur main, dev, ou feat/*
on:
  push:
    branches:
      - main
      - dev
      - 'feat/**'
  pull_request:
    branches:
      - main
      - dev

jobs:
  build-test:
    runs-on: ubuntu-latest

    steps:
      # 1️⃣ Checkout du code
      - name: Checkout repository
        uses: actions/checkout@v4

      # 2️⃣ Setup uv et Python
      - name: Install uv
        uses: astral-sh/setup-uv@v5
        with:
          enable-cache: true

      - name: Install Python 3.11
        run: uv python install 3.11

      - name: Install dependencies
        run: uv sync --all-extras --dev

      # 3️⃣ Linting avec Ruff
      - name: Lint code with Ruff
        run: uv run ruff check .

      # 4️⃣ Tests unitaires avec pytest et couverture
      - name: Run tests with pytest
        run: |
          uv run pytest --cov-report=xml
          uv run genbadge coverage -i coverage.xml -o coverage.svg

      - name: Commit coverage badge
        if: github.ref == 'refs/heads/main'
        run: |
          git config user.name "github-actions"
          git config user.email "github-actions@github.com"
          git add coverage.svg
          git commit -m "Update coverage badge" || echo "No changes"
          git push

      # 5️⃣ Scan de secrets avec Gitleaks
      - name: Run Gitleaks scan
        uses: gitleaks/gitleaks-action@v2
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

2) Se connecter a son compte sur DockerHub (https://hub.docker.com/)
   
    Pour créer un token DockerHub à utiliser comme secret GitHub (DOCKERHUB_PASSWORD).
    Clique sur ton avatar en haut à droite → Account Settings → Personnal access tokens
    - Donner un nom explicite à ton token (ex. GitHub Actions CD).
    - Choisir le scope “Read & Write” si tu veux pouvoir pusher des images depuis GitHub Actions.
    Clique sur Generate.
    ⚠️ Important : le token n’est affiché qu’une seule fois. Copie-le immédiatement.

3) Dans le repository du projet (https://github.com/)

Pour pouvoir push tes images, GitHub Actions doit se connecter à ton compte DockerHub.

Dans ton dépôt GitHub → Settings → Secrets → Actions
puis choisir “New repository secret” dans Repository secrets.
Ajouter :
- DOCKERHUB_USERNAME → ton nom d’utilisateur DockerHub
- DOCKERHUB_PASSWORD → ton mot de passe DockerHub ou un token d’accès

Dans le workflow, on utilise ces secrets :

```
- name: Log in to DockerHub
  uses: docker/login-action@v2
  with:
    username: ${{ secrets.DOCKERHUB_USERNAME }}
    password: ${{ secrets.DOCKERHUB_PASSWORD }}
```

4) Builder et pusher les images Docker

Ensuite, on construit l’image et on la pousse avec deux tags :

- latest → pour toujours avoir la dernière version.
- ${{ github.sha }} → pour versionner avec le hash du commit, utile pour revenir à une version précédente.

```
- name: Build and Push
  uses: docker/build-push-action@v5
  with:
    context: ./app_api          # dossier contenant le Dockerfile
    push: true                  # push automatique sur DockerHub
    tags: |
      ${{ secrets.DOCKERHUB_USERNAME }}/mon-api:latest
      ${{ secrets.DOCKERHUB_USERNAME }}/mon-api:${{ github.sha }}
```

=> creation du fichier .github\workflows\cd.yml

```
name: CD DockerHub

on:
  workflow_run:
    workflows: ["CI"]  # Nom exact de ton workflow CI
    types:
      - completed
    branches:
      - main

jobs:
  docker:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Log in to DockerHub
        uses: docker/login-action@v2
        with:
          username: ${{ secrets.DOCKERHUB_USERNAME }}
          password: ${{ secrets.DOCKERHUB_PASSWORD }}

      - name: Build and Push API image
        uses: docker/build-push-action@v5
        with:
          context: ./app_api         # dossier contenant le Dockerfile de l'API
          push: true
          tags: |
            ${{ secrets.DOCKERHUB_USERNAME }}/mon-api:latest
            ${{ secrets.DOCKERHUB_USERNAME }}/mon-api:${{ github.sha }}

      - name: Build and Push Front image
        uses: docker/build-push-action@v5
        with:
          context: ./app_front       # dossier contenant le Dockerfile du Front
          push: true
          tags: |
            ${{ secrets.DOCKERHUB_USERNAME }}/mon-front:latest
            ${{ secrets.DOCKERHUB_USERNAME }}/mon-front:${{ github.sha }}
```

4) pusher le code

- Surveille l’exécution du workflow CD en allant dans Actions → CD sur GitHub.
- À la fin, tes images doivent apparaître sur ton compte DockerHub (nico8760007/mon-api et nico8760007/mon-front).
- Tester tes images (facultatif) en récupérant l’image depuis n’importe quelle machine avec :
```
docker pull nico8760007/mon-api:latest
docker pull nico8760007/mon-front:latest
```

### Orchestration finale ###

creation du fichier `docker-compose.prod.yml` a la racine du projet.

commande en production :
```
docker compose -f docker-compose.prod.yml up -d
```
