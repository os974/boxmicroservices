# Projet 2 --- Orchestration, Sécurité et Livraison Continue

![CI Status](https://github.com/os974/boxmicroservices/actions/workflows/ci.yml/badge.svg)
![Coverage](https://raw.githubusercontent.com/os974/boxmicroservices/main/coverage.svg)
![Python](https://img.shields.io/badge/python-3.11-blue)
![Lint](https://img.shields.io/badge/lint-ruff-purple)
![License](https://img.shields.io/badge/license-MIT-green)

Ce projet transforme un simple script Python en une **architecture
micro‑services complète**, orchestrée avec Docker et automatisée via
GitHub Actions.

L'objectif est de construire une application composée de plusieurs
services indépendants capables de communiquer entre eux, de persister
les données et d'être déployés automatiquement.

------------------------------------------------------------------------

# Objectifs du Projet

Ce projet vise à maîtriser plusieurs concepts essentiels du
développement moderne :

-   Orchestration de services avec Docker Compose
-   Architecture micro‑services
-   Persistance des données avec PostgreSQL
-   Gestion sécurisée des variables d'environnement
-   Détection des fuites de secrets dans Git
-   Intégration Continue (CI)
-   Livraison Continue (CD)
-   Publication d'images Docker sur DockerHub

------------------------------------------------------------------------

# Architecture du Projet

L'application est composée de **trois services principaux** :

  Service    Technologie   Rôle
  ---------- ------------- -------------------------------------------
  Frontend   Streamlit     Interface utilisateur
  API        FastAPI       Traitement des requêtes et logique métier
  Database   PostgreSQL    Stockage persistant

Chaque service est isolé dans son conteneur Docker.

------------------------------------------------------------------------

# Structure du Dépôt

    .
    ├── .github/
    │   ├── workflows/
    │   │   ├── ci.yml
    │   │   └── cd.yml
    │
    ├── app_front/
    │   ├── main.py
    │   ├── pages/
    │   │   ├── 0_insert.py
    │   │   └── 1_read.py
    │   ├── pyproject.toml
    │   └── Dockerfile
    │
    ├── app_api/
    │   ├── main.py
    │   ├── Dockerfile
    │   ├── pyproject.toml
    │   │
    │   ├── models/
    │   │   └── models.py
    │   │
    │   ├── modules/
    │   │   ├── connect.py
    │   │   └── crud.py
    │   │
    │   ├── maths/
    │   │   └── mon_module.py
    │   │
    │   └── data/
    │       └── moncsv.csv
    │
    ├── tests/
    │   ├── test_api.py
    │   └── test_math_csv.py
    │
    ├── docker-compose.yml
    ├── docker-compose.prod.yml
    ├── conftest.py
    ├── .gitignore
    ├── .dockerignore
    └── .env.example

------------------------------------------------------------------------

# Fonctionnalités

## Frontend (Streamlit)

Interface utilisateur avec deux pages :

-   Page 1 --- Saisie de données
-   Page 2 --- Consultation des données enregistrées

Le frontend communique avec l'API via HTTP.

------------------------------------------------------------------------

## API (FastAPI)

L'API constitue le **cerveau de l'application**.

Routes principales :

POST /data\
Enregistre des données dans la base.

GET /data\
Récupère les données stockées.

------------------------------------------------------------------------

## Base de données

La base utilise **PostgreSQL** avec un **volume Docker persistant**.

Cela permet de conserver les données même si les conteneurs sont
arrêtés.

------------------------------------------------------------------------

# Développement Local

## 1 --- Cloner le projet

``` bash
git clone https://github.com/os974/AIToolbox.git
cd AIToolbox
```

------------------------------------------------------------------------

## 2 --- Créer les variables d'environnement

Créer un fichier `.env` à partir du template :

``` bash
cp .env.example .env
```

Exemple :

    POSTGRES_DB=mydb
    POSTGRES_USER=myuser
    POSTGRES_PASSWORD=mypassword
    DATABASE_URL=postgresql://myuser:mypassword@db:5432/mydb

------------------------------------------------------------------------

## 3 --- Lancer les services

``` bash
docker compose up --build
```

Services accessibles :

Frontend\
http://localhost:8501

API\
http://localhost:8000

Documentation API\
http://localhost:8000/docs

------------------------------------------------------------------------

# Tests

Les tests sont réalisés avec **Pytest**.

Lancer les tests :

``` bash
uv run pytest app_api/tests
```

Configuration dans `pyproject.toml` :

``` toml
[tool.pytest.ini_options]
pythonpath = ["."]
testpaths = ["tests"]
```

------------------------------------------------------------------------

# Gestion des Secrets

Les informations sensibles ne doivent jamais être versionnées.

Fichiers utilisés :

-   `.env`
-   `.env.example`
-   `.dockerignore`
-   `.gitignore`

Le fichier `.env` est exclu du dépôt Git.

------------------------------------------------------------------------

# Docker Compose

## Environnement de développement

docker-compose.yml construit les images localement.

------------------------------------------------------------------------

## Environnement de production

docker-compose.prod.yml télécharge directement les images depuis
DockerHub.

Exemple :

    image: username/project:latest

------------------------------------------------------------------------

# Intégration Continue (CI)

Pipeline GitHub Actions :

    .github/workflows/ci.yml

Étapes :

-   installation des dépendances
-   linting
-   exécution des tests
-   scan de sécurité Gitleaks

------------------------------------------------------------------------

# Sécurité --- Scan des Secrets

Un workflow dédié détecte les secrets accidentellement poussés dans Git.

Outil utilisé :

Gitleaks

Si un secret est détecté :

-   la CI échoue
-   le commit doit être nettoyé

------------------------------------------------------------------------

# Livraison Continue (CD)

Pipeline :

    .github/workflows/cd.yml

Déclenché uniquement si :

-   la CI est réussie
-   sur la branche `main`

Le workflow :

1.  se connecte à DockerHub
2.  build les images
3.  push les images

Tags utilisés :

    latest
    commit SHA

Exemple :

    username/app-api:latest
    username/app-api:9d3f2c8

------------------------------------------------------------------------

# Lancer la Version Production

``` bash
docker compose -f docker-compose.prod.yml up
```

Les images seront téléchargées automatiquement depuis DockerHub.

------------------------------------------------------------------------

# Bonnes Pratiques Implémentées

-   Architecture microservices
-   Isolation réseau Docker
-   Persistance des données
-   Gestion sécurisée des secrets
-   Tests automatisés
-   CI/CD automatisée
-   Versionnement des images Docker

------------------------------------------------------------------------

# Améliorations Possibles

-   Authentification utilisateur
-   Monitoring des services
-   Logs centralisés
-   Déploiement cloud
-   Scalabilité des services

------------------------------------------------------------------------

# Technologies Utilisées

Python\
FastAPI\
Streamlit\
PostgreSQL\
Docker\
Docker Compose\
GitHub Actions\
Pytest\
Gitleaks

------------------------------------------------------------------------

# License

Ce projet est sous licence **MIT**. Voir le fichier [LICENSE](LICENSE) pour plus de détails.

------------------------------------------------------------------------

# Auteur

Olivier Schollaert

------------------------------------------------------------------------

Projet réalisé dans le cadre d'un exercice de formation Simplon Dev IA / Data
Engineering visant à maîtriser :

-   orchestration
-   microservices
-   CI/CD
-   sécurité des pipelines
