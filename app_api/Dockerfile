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

# Lancement : on applique d'abord les migrations Alembic, puis on démarre
# uvicorn. Pourquoi via `sh -c` plutôt qu'un script séparé : suffisant
# pour 2 commandes ; à factoriser dans un entrypoint.sh si on ajoute des
# étapes (seed, warmup cache, etc.).
CMD ["sh", "-c", "alembic upgrade head && uvicorn main:app --host 0.0.0.0 --port 8000"]
