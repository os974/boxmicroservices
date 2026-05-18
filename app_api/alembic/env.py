"""Environnement Alembic.

Pourquoi ce fichier est custom :
- on récupère l'URL de connexion via le module `modules.connect` (même
  logique de résolution que l'API : DATABASE_URL > POSTGRES_* > fallback),
  pour qu'Alembic et l'API utilisent EXACTEMENT la même base ;
- on branche `target_metadata` sur `Base.metadata` après avoir importé les
  modèles, pour que `alembic revision --autogenerate` détecte les
  changements de schéma.
"""

import sys
from logging.config import fileConfig
from pathlib import Path

from alembic import context
from sqlalchemy import engine_from_config, pool

# Ajout du dossier app_api/ au sys.path : nécessaire pour que les imports
# `modules.connect` et `models.models` fonctionnent quand Alembic est
# lancé depuis ./app_api (ou depuis le container où WORKDIR=/app).
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from models.models import Operation  # noqa: F401  (import pour enregistrer la table)
from modules.connect import DATABASE_URL, Base

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Injection dynamique de l'URL résolue par notre module connect — évite
# de dupliquer la logique de connexion dans alembic.ini, et permet de
# garder alembic.ini sans secret.
config.set_main_option("sqlalchemy.url", DATABASE_URL)

# Source de vérité du schéma : le metadata SQLAlchemy de notre Base.
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Mode offline — génère du SQL sans connexion BDD (utile pour CI)."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Mode online — applique réellement les migrations sur la BDD cible."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
