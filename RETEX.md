# RETEX — Projet `boxmicroservices`

> Retour d'expérience à chaud après onboarding et premier `docker compose up`
> réussi sur une nouvelle machine. Objectif : capturer les frictions réelles
> et les décisions d'archi pendant qu'elles sont fraîches, pour soi-même et
> pour le prochain qui clone le repo.

## Contexte

Projet de formation Simplon Dev IA / Data Engineering : transformer un script
Python isolé en stack micro-services orchestrée. Trois services
(Streamlit + FastAPI + PostgreSQL), conteneurisés, avec CI/CD GitHub Actions,
scan de secrets Gitleaks et documentation Sphinx publiée sur GitHub Pages.

## Ce qui a bien marché

- **uv workspace** : un seul `uv sync --all-extras --dev` à la racine installe
  les deux membres + l'outillage dev. Pas de jonglage entre venvs.
- **Isolation réseau Compose** : deux réseaux nommés (`front-api`, `api-db`)
  empêchent le front d'atteindre la base directement — bonne pratique
  appliquée correctement.
- **Pipeline CI lisible** : 5 étapes claires (sync → ruff → pytest+coverage →
  badge → Gitleaks). La régénération automatique du badge `coverage.svg` sur
  `main` est élégante.
- **Tests sans Postgres** : `tests/conftest.py` injecte `DATABASE_URL` vers
  SQLite *avant* l'import de `app_api.modules.connect`. La CI tourne sans
  service DB à provisionner.
- **Secrets jamais commités** : `.env` exclu, `.env.example` fourni, Gitleaks
  bloque la CI en cas de fuite.

## Frictions rencontrées (vraies, pas théoriques)

| Friction | Cause racine | Coût |
|---|---|---|
| `docker compose up` → `unknown flag: --build` | Plugin `docker-compose-v2` non installé sur Ubuntu 24.04 | 10 min de debug confus (le message d'erreur ne dit pas que `compose` n'existe pas) |
| `permission denied … docker.sock` | Utilisateur pas dans le groupe `docker` | 5 min + nécessite déconnexion ou `newgrp` |
| `.env.example` avec **toutes les valeurs vides** | Template non opinionné | Premier `compose up` plante sans message clair sur la variable manquante |
| `tests/test_db.sqlite` trackée par git | Oubli dans `.gitignore` (`app_api/data/*.db` couvert, pas `tests/`) | Diff parasite à chaque run de tests, risque de commit de données de test |
| `DATABASE_URL` retombe en silence sur SQlite si les vars Postgres manquent | Fallback à 3 niveaux dans `connect.py` sans warning | Dangereux en prod : l'API démarre sur une base vide locale au lieu d'échouer |
| Badge coverage poussé directement sur `main` par github-actions | Workflow CI fait `git push` sur la branche protégée | Bypass involontaire des règles de PR ; surprend si la branche est protégée |

## Décisions d'architecture à expliciter

- **Pourquoi monorepo uv workspace plutôt que deux repos** : un seul lock,
  un seul pipeline CI, refacto inter-services possible sans PR coordonnée.
- **Pourquoi SQLite en test plutôt que Postgres conteneurisé** : tests qui
  tournent en < 1s, pas de service à attendre en CI. Compromis assumé : on
  ne valide pas les spécificités Postgres (types, contraintes, etc.).
- **Pourquoi `pythonpath = ["app_api", "app_front"]`** : permet aux modules
  d'importer en bare (`from modules.connect import …`) au lieu de
  `from app_api.modules.connect`. C'est ce qui fait que les Dockerfiles
  fonctionnent sans renommer les imports.
- **Pourquoi CD chaîné en `workflow_run` plutôt que dans le même workflow** :
  séparation propre des responsabilités, et le CD ne se redéclenche pas si
  on ré-exécute uniquement la CI.

## À reprendre la prochaine fois

**Bloquants à corriger en priorité :**
1. Renseigner `.env.example` avec des valeurs par défaut sûres et commentées
   (avec un avertissement clair "modifier en prod"), pour qu'un premier
   `compose up` aboutisse sans intervention.
2. Documenter les **prérequis système** dans le README (Docker Engine +
   plugin `docker-compose-v2`, appartenance au groupe `docker`).
3. `connect.py` : remplacer le fallback silencieux SQLite par un `raise` en
   l'absence des vars Postgres si on n'est pas en mode test (détecter via
   une var d'env explicite type `APP_ENV=test`).

**Améliorations à plus forte valeur :**
4. **API en body Pydantic** au lieu de query-params (`POST /data/?op=add&a=1`
   → `POST /data/` avec `OperationCreate(BaseModel)` et
   `Literal["add","sub","square"]`). Améliore validation, Swagger, et
   ergonomie côté front.
5. **Tests `app_front`** : la couverture pytest cible `app_api` uniquement,
   le front n'a aucun test.
6. **Healthchecks Compose** : `depends_on` n'attend pas que Postgres soit
   *prêt* (juste qu'il soit *démarré*). Premier appel API peut échouer.
   Ajouter `healthcheck` + `condition: service_healthy`.
7. **Gestion d'erreur frontend** : si l'API est down, le Streamlit crashe
   plutôt que d'afficher un message lisible.

**Hygiène repo :**
8. Pousser le `coverage.svg` via une action dédiée (avec un token scopé) au
   lieu d'un `git push` direct depuis le runner CI sur la branche protégée.
9. Ajouter `tests/*.sqlite` au `.gitignore` (fait).
10. Documenter dans le README la commande exacte de bootstrap
    (`uv sync --all-extras --dev` + `cp .env.example .env`).

## Métriques / état au moment du retex

- Couverture (badge actuel) : voir `coverage.svg`
- Services tournent : front `http://localhost:8501`, API `http://localhost:8000/docs`
- Branche : `main`, propre hors `.gitignore` mis à jour
- Stack validée localement : Docker Engine 29.1.3 + docker-compose-v2

---

*Document vivant — à compléter au fil des prochaines itérations.*
