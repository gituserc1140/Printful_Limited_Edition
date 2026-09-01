"""API client module for the Printful REST API.

This module provides a small request wrapper `make_request()` and a
`fetch_data()` function that calls the Printful API
(https://developers.printful.com/docs/). The API key and store id are
supplied by the caller (typically from Streamlit input fields) so nothing
sensitive needs to live in this file or in config/settings.py.
"""

import requests
from typing import Any, Dict, Optional
from config import settings


def build_headers(api_key: Optional[str] = None, store_id: Optional[str] = None) -> Dict[str, str]:
    """Build request headers for the Printful API.

    - Adds an Authorization header (token auth scheme) when an api_key
      is supplied (or falls back to settings.API_KEY).
    - Adds an `X-PF-Store-Id` header when a store_id is supplied, which is
      required for Printful accounts that manage multiple stores.
    """
    headers: Dict[str, str] = {}

    key = api_key or settings.API_KEY
    if key:
        headers["Authorization"] = "Bearer " + key.strip()

    if store_id:
        headers["X-PF-Store-Id"] = str(store_id).strip()

    return headers


def make_request(path: str, params: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None, method: str = "GET", timeout: Optional[int] = None) -> Any:
    """Simple HTTP request helper.

    - Builds a URL from settings.API_BASE_URL and path
    - Uses requests.request and returns parsed JSON
    - Raises on HTTP errors
    """
    base = settings.API_BASE_URL.rstrip("/")
    url = f"{base}/{path.lstrip('/')}"
    timeout = timeout or settings.DEFAULT_TIMEOUT
    headers = headers or {}

    resp = requests.request(method, url, params=params, headers=headers, timeout=timeout)
    resp.raise_for_status()

    # Attempt to parse JSON, fall back to raw text
    try:
        return resp.json()
    except ValueError:
        return resp.text


def _normalize_result(result: Any) -> Dict[str, Any]:
    """Normalize a Printful API response into the shape ui.render_home() expects.

    Printful responses typically look like:
      {"code": 200, "result": [...] or {...}, "paging": {...}, "error": {...}}
    """
    if isinstance(result, dict) and "error" in result and result.get("error"):
        error = result["error"]
        message = error.get("message") if isinstance(error, dict) else str(error)
        return {"title": "Printful API error", "description": message, "items": []}

    payload = result.get("result") if isinstance(result, dict) else result

    if isinstance(payload, list):
        items = []
        for entry in payload:
            if isinstance(entry, dict):
                items.append({
                    "id": entry.get("id"),
                    "name": entry.get("name") or entry.get("title") or str(entry.get("id")),
                    "value": entry.get("thumbnail_url") or entry.get("variants") or "",
                })
            else:
                items.append({"id": None, "name": str(entry), "value": ""})
        return {"title": "Printful result", "description": f"{len(items)} item(s) returned", "items": items}

    if isinstance(payload, dict):
        items = [{"id": k, "name": k, "value": v} for k, v in payload.items()]
        return {"title": "Printful result", "description": "Single object returned", "items": items}

    return {"title": "Printful result", "description": "Non-JSON response", "items": [{"id": 1, "name": str(payload), "value": 0}]}


def fetch_data(params: Optional[Dict[str, Any]] = None, api_key: Optional[str] = None, endpoint: Optional[str] = None, store_id: Optional[str] = None) -> Dict[str, Any]:
    """Call the Printful API and return a plain dict the UI can render.

    Args:
      params: query string parameters to forward to the endpoint (e.g.
        {"limit": 20, "offset": 0, "category_id": 24}).
      api_key: Printful API key/token. If omitted, falls back to
        settings.API_KEY (e.g. from the API_KEY environment variable).
      endpoint: Printful REST path to call, e.g. "store/products",
        "orders", "store". Defaults to settings.DEFAULT_ENDPOINT.
      store_id: Printful store id, forwarded as the X-PF-Store-Id header.
        Required for accounts with more than one store.

    Behavior:
      - If no api_key/API key is configured, returns a static example
        payload so the UI shows content without calling the real API.
      - Otherwise, calls the requested endpoint and normalizes the result.
    """
    params = params or {}
    endpoint = endpoint or settings.DEFAULT_ENDPOINT

    key = api_key or settings.API_KEY
    if not key:
        return {
            "title": "Printful Explorer sample",
            "description": "Enter a Printful API key to fetch real data from your store.",
            "items": [
                {"id": 1, "name": "Example product A", "value": 100},
                {"id": 2, "name": "Example product B", "value": 200},
            ],
        }

    # `key` is already resolved (api_key or settings.API_KEY); build_headers()'s
    # own settings.API_KEY fallback is a no-op here and only matters for callers
    # that invoke build_headers() directly with no api_key.
    headers = build_headers(api_key=key, store_id=store_id)

    try:
        result = make_request(path=endpoint, params=params, headers=headers)
        return _normalize_result(result)
    except Exception as exc:
        return {"title": "Error", "description": str(exc), "items": []}
