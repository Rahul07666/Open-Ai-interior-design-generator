# backend/utils.py
import os
import requests
from PIL import Image
from io import BytesIO

UNSPLASH_BASE = "https://api.unsplash.com"

def unsplash_search(query, per_page=15, access_key=None):
    """Search Unsplash for images matching query; returns list of image dicts."""
    if access_key is None:
        raise ValueError("Unsplash access key required")
    url = f"{UNSPLASH_BASE}/search/photos"
    params = {"query": query, "per_page": per_page, "orientation": "landscape"}
    headers = {"Accept-Version": "v1", "Authorization": f"Client-ID {access_key}"}
    r = requests.get(url, params=params, headers=headers, timeout=15)
    r.raise_for_status()
    data = r.json()
    return data.get("results", [])

def download_image_to_pil(url, timeout=15):
    r = requests.get(url, timeout=timeout)
    r.raise_for_status()
    return Image.open(BytesIO(r.content)).convert("RGB")
