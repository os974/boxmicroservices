"""Streamlit application entry point.

This module initializes the main interface of the frontend application.
It provides a simple landing page explaining the purpose of the app.

The frontend communicates with the FastAPI backend to:
- Insert new mathematical operations
- Retrieve stored operations from the database
"""

import streamlit as st

st.set_page_config(
    page_title="Math Operations App",
    page_icon="🧮",
    layout="centered",
)

st.title("Math Operations Application")

st.write(
    """
This Streamlit application allows users to interact with a backend API
that stores mathematical operations in a database.

Available features:
- Insert new mathematical operations
- View previously stored operations
"""
)

st.info(
    "Use the navigation menu on the left to insert or view operations."
)
