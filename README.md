# Printful Explorer

A lightweight Streamlit app for interacting with the
[Printful API](https://developers.printful.com/docs/). Enter your Printful
API key (and store id, if needed) directly in the app, adjust the endpoint
and query parameters, and fetch live data from your Printful account.

Contents
- app.py — Streamlit entrypoint that collects the API key, store id,
  endpoint, and query parameters, then calls api_client.fetch_data()
- api_client.py — API client module with a `make_request()` helper and a
  `fetch_data()` function that calls the Printful REST API
- ui.py — UI layout module that renders the returned data using Streamlit
- config/ — configuration module with default settings (base URL, default
  endpoint, timeout)
- requirements.txt — minimal dependencies

Quick start
1. Install dependencies
   pip install -r requirements.txt

2. Run locally
   streamlit run app.py

3. In the app, paste your Printful API key (from your Printful
   [Developer Portal](https://developers.printful.com/)), optionally set a
   store id, choose an endpoint (defaults to `store/products`), and add any
   query parameters as JSON (e.g. `{"limit": 20, "offset": 0}`).

Using the app
- The primary integration point is api_client.fetch_data(). It accepts an
  API key, store id, endpoint, and params, calls the Printful API, and
  normalizes the response into a shape ui.render_home() can display.
- config/settings.py contains defaults for API_BASE_URL
  (`https://api.printful.com`) and DEFAULT_ENDPOINT (`store/products`). You
  can override these with environment variables or provide values at
  runtime via the Streamlit app input fields.
- ui.py contains simple rendering logic with Streamlit. Modify or replace it
  to match your UI needs (components, layout, charts, etc.).

Extending the app
- Add more Printful-specific parameters/endpoints as needed (e.g. orders,
  sync variants, webhooks) — see the
  [Printful API docs](https://developers.printful.com/docs/) for the full
  list.
- Add tests for api_client.fetch_data() and UI rendering logic.
- Add a Dockerfile or GitHub Actions workflow for CI and deployment.

License
Add a LICENSE file appropriate for your project.
