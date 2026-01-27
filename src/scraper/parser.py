import time
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from src.config import Config, PostPaginationMode
from src.scraper.models import Category, Thread, Post


def parse_category(content: BeautifulSoup, pagination_threads) -> Category:
    text = content.find_all("p")
    name = text[0].get_text(strip=True)
    description = text[1].get_text(strip=True)
    badges = content.find_all("span", class_="badge")
    threads = None
    posts = None
    if len(badges) >= 2:
        threads = badges[0].get_text(strip=True)
        posts = badges[1].get_text(strip=True)
    relative_url = content.get("href")
    url = [urljoin(Config.forum_url.value, relative_url)]
    if pagination_threads:
        url = get_paginated_url( "all", url)

    return Category(name, description, threads, posts, url)

def parse_thread(content: BeautifulSoup, post_pagination: PostPaginationMode) -> Thread:
    name_tag = content.find("p")
    name = name_tag.get_text(strip=True) if name_tag else ""
    comments_tag = content.select_one("span.badge.bg-info.text-dark")
    likes_tag = content.select_one("span.badge.bg-warning.text-dark")
    comments = comments_tag.get_text(strip=True) if comments_tag else "0"
    likes = likes_tag.get_text(strip=True) if likes_tag else "0"
    a = content.find("a", class_="card-link")
    relative_url = a.get("href")
    thread_url = urljoin(Config.forum_url.value, relative_url)
    thread_url = get_paginated_url(post_pagination, thread_url)
    return Thread(name, comments, likes, thread_url)

def parse_post(content: BeautifulSoup):
    posts_ids= []
    post_list = []
    posts = content.find_all("div", class_="post-item mb-3")
    for post in posts:
        post_id = post.get("id")
        if post_id not in posts_ids:
            posts_ids.append(post_id)
            date_time = (
                post.find("small").get_text(strip=True)
                if post.find("small")
                else ""
            )
            content_section = post.find_next("div", class_="post-content mb-3")
            if content_section.find("Quote nested-0"):
                post_content = extract_clean_response(content_section)
            else:
                post_content = [p.get_text(strip=True) for p in content_section]
            c_likes = post.find(
                "button", class_="btn btn-outline-primary likePostBtn btn-sm"
            )
            likes_tag = c_likes.find("span") if c_likes else None
            try:
                likes = int(likes_tag.get_text(strip=True)) if likes_tag else 0
            except ValueError:
                likes = 0
            post_list.append(Post(post_id, date_time, post_content, likes))
    return post_list


def extract_clean_response(post_content):
    for quote in post_content.find_all('blockquote'):
        quote.decompose()
    for tag in post_content.find_all(['a', 'img']):
        tag.decompose()
    return post_content.get_text(strip=True)

def get_paginated_url( mode, base_url):
    raw = get_page_html(base_url)
    url_list = [base_url]
    content = BeautifulSoup(raw, 'html.parser')
    if content.find("a", class_="page-link", attrs={"aria-label": "Last"}):
        last_page = content.find("a", class_="page-link", attrs={"aria-label": "Last"}).get("href")
        integ_last_page = int(last_page[-1])
        page_number = 2
        if mode == "last_two":
            if integ_last_page > 2:
                page_number = integ_last_page -1
        while page_number <= integ_last_page:
            extension = "?page="+str(page_number)
            next_url = base_url +extension
            url_list.append(next_url)
            page_number += 1
    return url_list

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





