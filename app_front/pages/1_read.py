"""Streamlit page used to display stored operations.

This page retrieves all mathematical operations stored in the
database by calling the FastAPI backend API.

The retrieved data is displayed in a tabular format using
a pandas DataFrame.
"""

import os

import pandas as pd
import requests
import streamlit as st
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Lire l'hôte de l'API depuis l'environnement
API_HOST = os.getenv("API_HOST", "127.0.0.1")
API_URL = f"http://{API_HOST}:8000/data"

st.title("Stored Mathematical Operations")

if st.button("Load operations"):
    try:
        response = requests.get(API_URL)

        if response.status_code == 200:
            data = response.json()

            if len(data) == 0:
                st.warning("No operations found in the database.")
            else:
                df = pd.DataFrame(data)
                st.dataframe(df)

        else:
            st.error("Error while retrieving operations.")

    except requests.exceptions.ConnectionError:
        st.error("Unable to connect to the API. Make sure FastAPI is running.")
