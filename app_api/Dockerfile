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
