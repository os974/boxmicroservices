# Projet 2 --- Orchestration, Sécurité et Livraison continue

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

Routes principales (versionnées sous `/v1/data/`) :

| Méthode | Endpoint | Description |
|---|---|---|
| `POST` | `/v1/data/` | Insérer une opération (body JSON validé par Pydantic) |
| `GET` | `/v1/data/` | Lister toutes les opérations |
| `PUT` | `/v1/data/{id}` | Mettre à jour une opération |
| `DELETE` | `/v1/data/{id}` | Supprimer une opération |
| `GET` | `/` | Sanity check |

Le body attendu en POST/PUT :

```json
{"operation": "add", "a": 1, "b": 2}
```

`operation` doit être `"add"`, `"sub"` ou `"square"` (validation
Pydantic via `Literal` — toute autre valeur est rejetée en 422).
`b` est optionnel pour `square` (opération unaire).

La documentation interactive complète est exposée par FastAPI sur
[http://localhost:8000/docs](http://localhost:8000/docs) une fois la
stack lancée.

------------------------------------------------------------------------

## Base de données

La base utilise **PostgreSQL** avec un **volume Docker persistant**.

Cela permet de conserver les données même si les conteneurs sont
arrêtés.

------------------------------------------------------------------------

# Développement Local

## 1 --- Cloner le projet

``` bash
git clone https://github.com/os974/boxmicroservices.git
cd boxmicroservices
```

------------------------------------------------------------------------

## 2 --- Créer les variables d'environnement

Créer un fichier `.env` à partir du template :

``` bash
cp .env.example .env
```

Le template est opinionné — valeurs par défaut sûres pour le dev local
(Postgres / `postgres` / `mydb` / réseau Compose). À éditer uniquement
en prod (et alors utiliser un secret manager, pas un `.env` versionné).

# Gestion des Secrets

Les informations sensibles ne doivent jamais être versionnées.

Fichiers utilisés :

-   `.env` (local, exclu du repo)
-   `.env.example` (template versionné)
-   `.dockerignore`
-   `.gitignore`

Pour détecter une fuite accidentelle, deux filets sont en place :
**Gitleaks** dans la CI (cf. `.github/workflows/ci.yml`) et un hook
**pre-commit local** (cf. étape 3 ci-dessous) — il bloque le commit
avant même le push si un secret est détecté.

------------------------------------------------------------------------

## 3 --- (optionnel) Activer les hooks pre-commit

Pour bénéficier du lint Ruff + scan Gitleaks **avant chaque commit**
plutôt qu'attendre la CI :

``` bash
uv tool install pre-commit       # une fois par machine
pre-commit install               # active les hooks dans ce repo
```

Skip ponctuel : `git commit --no-verify` (à justifier).

------------------------------------------------------------------------

## 4 --- Lancer les services

# Docker Compose

## Environnement de développement

docker-compose.yml construit les images localement. Au démarrage,
l'API exécute automatiquement `alembic upgrade head` avant uvicorn
(cf. `app_api/Dockerfile`) — pas d'étape manuelle de migration.

``` bash
docker compose up --build
```

### Démarrage hors Docker (rare, dev pur Python)

Si l'on veut lancer l'API directement avec `uvicorn` (sans Docker),
appliquer **manuellement** les migrations Alembic d'abord — sinon la
table `operations` n'existe pas et tout POST renvoie 500 :

``` bash
cd app_api
uv run alembic upgrade head
uv run uvicorn main:app --reload
```

> ⚠️ Piège SQLite : `settings.database_url` vaut par défaut
> `sqlite:///./local.sqlite` — un chemin **relatif au cwd**. Lancer
> `alembic` et `uvicorn` depuis le même dossier (`app_api/`), sinon
> ils pointent sur deux fichiers différents. En Compose (Postgres),
> ce problème n'existe pas.

## Environnement de production

docker-compose.prod.yml télécharge directement les images depuis
DockerHub.

``` bash
docker compose -f docker-compose.prod.yml up
```

Exemple :

    image: username/project:latest

Services accessibles :

Frontend Streamlit pour les formules mathématiques\
http://localhost:8501

API\
http://localhost:8000

Documentation Swagger API\
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

# Documentation

La documentation technique est générée avec **Sphinx** et déployée via **GitHub Pages**.
Elle est accessible à l'adresse suivante : [Lien vers la documentation](https://os974.github.io/boxmicroservices/).

Pour la générer localement :
```bash
uv run sphinx-build docs/source public
```

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
