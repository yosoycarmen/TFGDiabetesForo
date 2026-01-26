import html
import time

import requests
from bs4 import BeautifulSoup

from src.scraper import parser


def get_page_html(url: str):
    last_exc: requests.RequestException | None = None
    session = requests.Session()
    for attempt in range(3):
        try:
            response = session.get(url, timeout=10)
            response.raise_for_status()
            raw = response.text
            return raw
        except requests.RequestException as exc:
            last_exc = exc
            time.sleep(0.5 * (attempt + 1))
    if last_exc:
        print(f"Error al obtener la página {url}: {last_exc}")
    return ""


def fetch_category(content: BeautifulSoup):
    category = parser.parse_category(content)
    return category


def fetch_thread(content: BeautifulSoup):
    thread = parser.parse_thread(content)
    return thread


def fetch_posts(content: BeautifulSoup):
    post = parser.parse_post(content)
    return post
