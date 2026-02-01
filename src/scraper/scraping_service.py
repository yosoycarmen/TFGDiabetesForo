from concurrent.futures import ThreadPoolExecutor, as_completed
import os
from pathlib import Path

from bs4 import BeautifulSoup

from src.config import Config, PostPaginationMode, ScrapingMode
from src.etl import build_clean_posts
from src.etl.build_clean_posts import DataCleaner
from src.scraper import scraper
from src.scraper.models import Category, Thread, Post
from src.scraper.scraper import fetch_category, fetch_thread, fetch_posts

import pandas as pd


class ScrapingService:

    def __init__(self, max_workers: int | None = None):
        self.categories_df = pd.DataFrame()
        self.threads_df = pd.DataFrame()
        self.posts_df = pd.DataFrame()
        self.max_workers = max_workers or self._default_max_workers()

    @staticmethod
    def _default_max_workers() -> int:
        return min(32, (os.cpu_count() or 1) * 5)



    def run_scraping(self, mode: ScrapingMode = ScrapingMode.FULL):
        if mode == ScrapingMode.LATEST:
            self.run_latest_posts_scraping()
        elif mode in (ScrapingMode.FULL_1, ScrapingMode.FULL_2, ScrapingMode.FULL_3):
            segment = int(mode.value.split()[-1])
            self.run_full_scraping(category_segment=segment)
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


    def run_full_scraping(self, category_segment: int | None = None):
        self.save_categories(
            paginate_threads=True,
            post_pagination=PostPaginationMode.ALL,
            category_segment=category_segment,
        )
        self._write_csv(self.categories_df, Path(Config.raw_categories_file.value))
        self._write_csv(self.threads_df, Path(Config.raw_threads_file.value))
        self._write_csv(self.posts_df, Path(Config.raw_posts_file.value))



    def save_categories(self,
        paginate_threads: bool,
        post_pagination: PostPaginationMode,
        category_segment: int | None = None,) :
        raw = scraper.get_page_html(Config.forum_categories_url.value)
        categories = BeautifulSoup(raw, 'html.parser')
        categories = categories.find_all("a", class_="card-link")
        categories = list(categories)
        if category_segment is not None:
            start, end = self._category_segment_range(len(categories), category_segment)
            categories = categories[start:end]
        for category_content in categories:
            category = fetch_category(category_content, paginate_threads)
            self.category_to_dataframe(category)
            self.save_threads(category.url, category.name, post_pagination)



    def save_threads(self, url, category_name: str, post_pagination: PostPaginationMode) -> None:
        threads_to_fetch: list[Thread] = []
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {
                executor.submit(scraper.get_page_html, url_pag): url_pag
                for url_pag in url
            }
            for future in as_completed(futures):
                raw = future.result()
                if not raw:
                    continue
                threads = BeautifulSoup(raw, 'html.parser')
                thread_soup = threads.select("div.col-md-4.mb-4")
                for threads_content in thread_soup:
                    thread = fetch_thread(threads_content, post_pagination)
                    thread.category = category_name
                    threads_to_fetch.append(thread)

        for thread in threads_to_fetch:
            self.thread_to_dataframe(thread)
            self.save_posts(thread.url, thread.title, category_name)

    def save_posts(self, url, thread_name: str, category_name: str) -> None:
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {
                executor.submit(scraper.get_page_html, url_pag): url_pag
                for url_pag in url
            }
            for future in as_completed(futures):
                raw = future.result()
                if not raw:
                    continue
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
            "category": thread.category,
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
            "category" : post.category,
            "thread": post.thread,
        }]
        post_data = pd.DataFrame(post_data)
        self.posts_df = pd.concat([self.posts_df, post_data], ignore_index=True)



    def _write_csv(self, df: pd.DataFrame, path: Path) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(path.suffix + ".tmp")
        df.to_csv(tmp, index=False, encoding="utf-8", lineterminator="\n")
        tmp.replace(path)

    @staticmethod
    def _category_segment_range(total_categories: int, segment: int) -> tuple[int, int]:
        if segment not in (1, 2, 3):
            raise ValueError("segment must be 1, 2, or 3")
        if total_categories <= 0:
            return (0, 0)
        base_size = total_categories // 3
        remainder = total_categories % 3
        sizes = [
            base_size + (1 if index < remainder else 0)
            for index in range(3)
        ]
        start = sum(sizes[:segment - 1])
        end = start + sizes[segment - 1]
        return (start, end)

if __name__ == "__main__":
    scrape_runer = ScrapingService()
    scrape_runer.run_scraping()
    cleaner = DataCleaner()
    cleaner.clean_dataset()
