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
