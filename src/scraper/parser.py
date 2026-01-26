from urllib.parse import urljoin

from bs4 import BeautifulSoup

from src.config import Config
from src.scraper.models import Category, Thread, Post


def parse_category(content: BeautifulSoup) -> Category:
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
    url = urljoin(Config.forum_url.value, relative_url)
    return Category(name, description, threads, posts, url)

def parse_thread(content: BeautifulSoup) -> Thread:
    name_tag = content.find("p")
    name = name_tag.get_text(strip=True) if name_tag else ""
    comments_tag = content.select_one("span.badge.bg-info.text-dark")
    likes_tag = content.select_one("span.badge.bg-warning.text-dark")
    comments = comments_tag.get_text(strip=True) if comments_tag else "0"
    likes = likes_tag.get_text(strip=True) if likes_tag else "0"
    a = content.find("a", class_="card-link")
    relative_url = a.get("href")
    thread_url = urljoin(Config.forum_url.value, relative_url)
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





