"""Streamlit page used to insert mathematical operations.

This page provides a form allowing the user to create a new
mathematical operation. The operation is sent to the FastAPI backend
via an HTTP POST request.

Supported operations:
- add
- sub
- square

The backend API stores the operation in a SQLite database.
"""

import os

import requests
import streamlit as st
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Lire l'hôte de l'API depuis l'environnement
API_HOST = os.getenv("API_HOST", "127.0.0.1")
API_URL = f"http://{API_HOST}:8000/data"

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
