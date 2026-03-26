# Simplon Projet 2 – Toolbox Microservice

![CI Status](https://github.com/nicolastchenio/simplon_projet2_toolbox_microService/actions/workflows/ci.yml/badge.svg)
![Coverage](https://raw.githubusercontent.com/nicolastchenio/simplon_projet2_toolbox_microService/main/coverage.svg)
![Python](https://img.shields.io/badge/python-3.11-blue)
![Lint](https://img.shields.io/badge/lint-ruff-purple)
![License](https://img.shields.io/badge/license-MIT-green)

## Overview

**Python Toolbox Microservice** est une architecture modulaire et distribuée démontrant la mise en place d'un système micro-services complet, sécurisé et orchestré. Le projet se compose d'une API de calcul mathématique et d'une interface utilisateur interactive, le tout géré au sein d'un monorepo.

### Points clés :
- **Architecture Monorepo** gérée avec `uv` pour une gestion efficace des dépendances.
- **Backend API** performant avec FastAPI, supportant les opérations CRUD.
- **Frontend Interactif** avec Streamlit pour une manipulation aisée des données.
- **Persistance des données** : Utilisation de PostgreSQL en production avec un fallback automatique vers SQLite pour le développement local.
- **Conteneurisation** : Dockerisation complète des services pour un déploiement reproductible.
- **CI/CD & Sécurité** : Pipeline automatisée avec tests, linting (Ruff), scan de secrets (Gitleaks) et déploiement Docker Hub.

---

## Project Structure

```plaintext
.
├── .github/                    
│   ├── workflows/
│   │   ├── ci.yml             # Linting, Tests, Gitleaks
│   │   ├── cD.yml             # Build & Push DockerHub
│   │   └── docs.yml           # Documentation Sphinx
│   └── CODE_OF_CONDUCT.md
│   └── CONTRIBUTING.md          
├── app_api/                   # Service Backend (FastAPI)
│   ├── maths/                 # Logique métier mathématique
│   ├── models/                # Modèles de données (Pydantic/SQLAlchemy)
│   ├── modules/               # Connexion et CRUD
│   ├── data/                  # Données statiques (CSV)
│   └── main.py                # Point d'entrée de l'API
├── app_front/                 # Service Frontend (Streamlit)
│   ├── pages/                 # Pages de saisie et d'affichage
│   └── main.py                # Point d'entrée du Front
├── tests/                     # Tests globaux (API et Logique)
│   ├── conftest.py
│   ├── test_api.py
│   ├── test_db.sqlite
│   └── test_math_csv.py   
├── docs/                      # Documentation technique (Sphinx)
├── .dockerignore 
├── .gitignore 
├── docker-compose.yml         # Pour le développement (build: .)
├── docker-compose.prod.yml    # Pour la prod (image: user/repo:tag)
├── pyproject.toml             # Configuration du Monorepo (uv workspace)
├── uv.lock                    
├── README.md
└── LICENSE
```

---

## Fonctionnalités

### API Backend (FastAPI)
L'API expose des points de terminaison pour gérer des opérations mathématiques :
- **POST `/data/`** : Créer une nouvelle opération (add, sub, square).
- **GET `/data/`** : Lister toutes les opérations enregistrées.
- **PUT `/data/{id}`** : Mettre à jour une opération existante.
- **DELETE `/data/{id}`** : Supprimer une opération.
- **Documentation Swagger** : Disponible sur `/docs`.

### Frontend (Streamlit)
Une interface utilisateur intuitive permettant de :
- **Insérer** des opérations via un formulaire dédié.
- **Visualiser** l'historique des calculs sous forme de tableau (Pandas DataFrame).

---

## Installation & Utilisation (Local)

### 1. Prérequis
- Python 3.11
- `uv` installé (`pip install uv`)

### 2. Clonage et Configuration
```bash
git clone https://github.com/nicolastchenio/simplon_projet2_toolbox-microservice.git
cd simplon_projet2_toolbox-microservice
uv sync
```

### 3. Lancement des services
Vous devez lancer l'API et le Front dans deux terminaux séparés :

**Terminal 1 : API**
```bash
uv run uvicorn app_api.main:app --reload
```

- API : http://127.0.0.1:8000
- Documentation interactive (Swagger) : http://127.0.0.1:8000/docs

**Terminal 2 : Frontend**
```bash
cd app_front
uv run streamlit run main.py
```
- Interface Utilisateur : http://localhost:8501

---

## Déploiement avec Docker

Le projet propose deux configurations Docker Compose :

### Développement (Build local)
Utilise les fichiers locaux pour construire les images :
```bash
docker-compose up --build
```

### Production (Images Docker Hub)
Utilise les images pré-construites sur Docker Hub :
```bash
docker-compose -f docker-compose.prod.yml up
```
*Note : Assurez-vous d'avoir configuré les variables d'environnement dans un fichier `.env`.*

---

## Tests & Qualité de code

### Exécuter les tests
```bash
uv run pytest
```

### Couverture de code
```bash
uv run pytest --cov=app_api --cov-report=term-missing
```

### Linting (Ruff)
```bash
uv run ruff check .
```

---

## Documentation

La documentation technique est générée avec **Sphinx** et déployée via **GitHub Pages**.
Elle est accessible à l'adresse suivante : [Lien vers la documentation](https://nicolastchenio.github.io/simplon_projet2_toolbox_microService/) (à adapter selon l'URL réelle).

Pour la générer localement :
```bash
uv run sphinx-build docs/source public
```

---

## CI/CD & Sécurité

- **CI (GitHub Actions)** : Exécute Ruff, Pytest, génère le badge de couverture et scanne les secrets avec **Gitleaks**.
- **CD (Docker Hub)** : Construit et pousse automatiquement les images `mon-api` et `mon-front` vers Docker Hub après succès de la CI sur la branche `main`.
- **Docs** : Déploiement automatique sur GitHub Pages.

---

## Contributeurs
- Nicolas Tchenio

## License
Ce projet est sous licence **MIT**. Voir le fichier [LICENSE](LICENSE) pour plus de détails.
