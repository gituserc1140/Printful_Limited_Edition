"""Streamlit-based Printful API explorer entrypoint.

Gathers minimal user inputs (Printful API key, store id, endpoint, and
query parameters) and calls api_client.fetch_data() as the integration
point with the Printful REST API (https://developers.printful.com/docs/).
The UI is rendered via ui.render_home().

Run locally:
  pip install -r requirements.txt
  streamlit run app.py
"""

import json

import streamlit as st
from config import settings
import api_client
import ui

st.set_page_config(page_title="Printful Explorer", layout="centered")

st.header("Printful Explorer")
st.write(
    "A lightweight Streamlit app for exploring the Printful API "
    "(https://developers.printful.com/docs/)."
)

# Credentials: kept in the UI only, never persisted to disk.
api_key = st.text_input("Printful API key", value="", type="password")
store_id = st.text_input(
    "Store ID (optional)",
    value="",
    help="Required if your Printful account has more than one store.",
)

# Printful-specific parameters, editable by the end user.
endpoint = st.text_input(
    "Endpoint",
    value=settings.DEFAULT_ENDPOINT,
    help="Printful REST path to call, e.g. store/products, orders, store.",
)
params_input = st.text_area(
    "Query parameters (JSON)",
    value='{}',
    help='Optional JSON object forwarded as query params, e.g. {"limit": 20, "offset": 0}',
)

if st.button("Fetch data"):
    try:
        params = json.loads(params_input or "{}")
    except Exception as exc:
        st.error(f"Could not parse parameters as JSON: {exc}")
        params = {}

    data = api_client.fetch_data(
        params=params,
        api_key=api_key or None,
        endpoint=endpoint or None,
        store_id=store_id or None,
    )

    ui.render_home(data)
else:
    st.info(
        "Enter your Printful API key (and store id, if applicable), "
        "adjust the endpoint/parameters, then click Fetch data."
    )
