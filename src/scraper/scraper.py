import html
import time

import requests
from bs4 import BeautifulSoup

from src.config import PostPaginationMode
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


def fetch_category(content: BeautifulSoup, pagination_threads: bool):
    category = parser.parse_category(content, pagination_threads)
    return category


def fetch_thread(content: BeautifulSoup, post_pagination : PostPaginationMode):
    thread = parser.parse_thread(content, post_pagination)
    return thread


def fetch_posts(content: BeautifulSoup):
    post = parser.parse_post(content)
    return post
