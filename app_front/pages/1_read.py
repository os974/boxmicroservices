"""Page Streamlit — consultation des opérations stockées.

Récupère toutes les opérations via `GET /v1/data/` et les affiche dans
un DataFrame pandas.
"""

import os

import pandas as pd
import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

API_HOST = os.getenv("API_HOST", "127.0.0.1")
API_URL = f"http://{API_HOST}:8000/v1/data/"

st.title("Stored Mathematical Operations")

if st.button("Load operations"):
    try:
        response = requests.get(API_URL, timeout=5)

        if response.status_code == 200:
            data = response.json()
            if len(data) == 0:
                st.warning("No operations found in the database.")
            else:
                df = pd.DataFrame(data)
                st.dataframe(df)
        else:
            st.error(f"Error {response.status_code} : {response.text}")

    except requests.exceptions.ConnectionError:
        st.error("Unable to connect to the API. Make sure FastAPI is running.")
