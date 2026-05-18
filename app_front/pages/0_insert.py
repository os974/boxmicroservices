"""Page Streamlit — insertion d'une opération mathématique.

Cette page construit un formulaire et POSTe un payload JSON à l'API
FastAPI (`POST /v1/data/`). Opérations supportées : add / sub / square.
"""

import os

import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

# Lecture de l'hôte API depuis l'environnement.
# - en Compose : API_HOST=api (nom de service du réseau front-api)
# - hors Compose : API_HOST=localhost (ou laisser tomber sur le défaut)
API_HOST = os.getenv("API_HOST", "127.0.0.1")
API_URL = f"http://{API_HOST}:8000/v1/data/"

st.title("Insert a Mathematical Operation")

operation = st.selectbox("Select operation", ["add", "sub", "square"])
a = st.number_input("Value A", value=0.0)

# `square` est unaire — on n'affiche le champ B que pour add/sub, et on
# laisse `b = None` sinon (Pydantic acceptera l'absence du champ).
b = None
if operation != "square":
    b = st.number_input("Value B", value=0.0)

if st.button("Submit operation"):
    # Body JSON (et non plus query-params) : le contrat API attend un
    # OperationCreate validé par Pydantic côté serveur.
    payload = {"operation": operation, "a": a, "b": b}

    try:
        response = requests.post(API_URL, json=payload, timeout=5)

        if response.status_code == 200:
            st.success("Operation successfully stored.")
            st.json(response.json())
        else:
            # On affiche le détail de l'erreur API (validation Pydantic 422
            # ou erreur métier 400) pour faciliter le debug côté utilisateur.
            st.error(f"Error {response.status_code} : {response.text}")

    except requests.exceptions.ConnectionError:
        st.error("Unable to connect to the API. Make sure FastAPI is running.")
