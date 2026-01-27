from pathlib import Path

from bs4 import BeautifulSoup

from src.config import Config, PostPaginationMode, ScrapingMode
from src.scraper import scraper
from src.scraper.models import Category, Thread, Post
from src.scraper.scraper import fetch_category, fetch_thread, fetch_posts

import pandas as pd


class ScrapingService:

    def __init__(self):
        self.categories_df = pd.DataFrame()
        self.threads_df = pd.DataFrame()
        self.posts_df = pd.DataFrame()



    def run_scraping(self, mode: ScrapingMode = ScrapingMode.FULL):
        if mode == ScrapingMode.LATEST:
            self.run_latest_posts_scraping()
        else:
            self.run_full_scraping()


    def run_latest_posts_scraping(self):
        self.save_categories(
            paginate_threads=False,
            post_pagination=PostPaginationMode.LAST_TWO,
        )
        self._write_csv(self.categories_df, Path(Config.raw_categories_file.value))
        self._write_csv(self.threads_df, Path(Config.raw_threads_file.value))
        self._write_csv(self.posts_df, Path(Config.raw_posts_file.value))


    def run_full_scraping(self):
        self.save_categories(
            paginate_threads=True,
            post_pagination=PostPaginationMode.ALL,
        )
        self._write_csv(self.categories_df, Path(Config.raw_categories_file.value))
        self._write_csv(self.threads_df, Path(Config.raw_threads_file.value))
        self._write_csv(self.posts_df, Path(Config.raw_posts_file.value))



    def save_categories(self,
        paginate_threads: bool,
        post_pagination: PostPaginationMode,) :
        raw = scraper.get_page_html(Config.forum_categories_url.value)
        categories = BeautifulSoup(raw, 'html.parser')
        categories = categories.find_all("a", class_="card-link")
        for category_content in categories:
            category = fetch_category(category_content, paginate_threads)
            self.category_to_dataframe(category)
            self.save_threads(category.url, category.name, post_pagination)



    def save_threads(self, url, category_name: str, post_pagination: PostPaginationMode) -> None:
        for url_pag in url:
            raw = scraper.get_page_html(url_pag)
            threads = BeautifulSoup(raw, 'html.parser')
            thread_soup = threads.select("div.col-md-4.mb-4")
            for threads_content in thread_soup:
                thread = fetch_thread(threads_content, post_pagination)
                thread.category = category_name
                self.thread_to_dataframe(thread)
                self.save_posts(thread.url, thread.title, category_name)

    def save_posts(self, url, thread_name: str, category_name: str) -> None:
        for url_pag in url:
            raw = scraper.get_page_html(url_pag)
            posts = BeautifulSoup(raw, 'html.parser')
            posts_list = fetch_posts(posts)
            for post in posts_list:
                post.category = category_name
                post.thread = thread_name
                self.post_to_dataframe(post)

    def category_to_dataframe(self, category: Category):
        category_data = [
            {
                "name": category.name,
                "description": category.description,
                "threads": category.threads,
                "post": category.posts,
                "url": category.url,
            }
        ]
        category_data = pd.DataFrame(category_data)
        self.categories_df = pd.concat([self.categories_df, category_data], ignore_index=True)
    def thread_to_dataframe(self, thread: Thread):
        thread_data = [{
            "name": thread.title,
            "comments": thread.comments,
            "likes": thread.likes,
            "url": thread.url,
        }]
        thread_data = pd.DataFrame(thread_data)
        self.threads_df = pd.concat([self.threads_df, thread_data], ignore_index=True)

    def post_to_dataframe(self, post: Post):
        post_data = [{
            "post_id": post.post_id,
            "timestamp": post.timestamp,
            "content": post.content,
            "likes": post.likes,
        }]
        post_data = pd.DataFrame(post_data)
        self.posts_df = pd.concat([self.posts_df, post_data], ignore_index=True)



    def _write_csv(self, df: pd.DataFrame, path: Path) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(path.suffix + ".tmp")
        df.to_csv(tmp, index=False, encoding="utf-8", lineterminator="\n")
        tmp.replace(path)

if __name__ == "__main__":
    scraping_service = ScrapingService()
    scraping_service.run_scraping(ScrapingMode.LATEST)


