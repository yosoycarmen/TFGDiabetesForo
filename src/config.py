from enum import Enum
from pathlib import Path


class Config(Enum):
    forum_url = "https://diabetesforo.com/es/"
    forum_categories_url = "https://diabetesforo.com/es/categories/"
    raw_posts_file = "data/raw_posts.csv"
    raw_threads_file = "data/raw_threads.csv"
    raw_categories_file = "data/raw_categories.csv"

class ScrapingMode(Enum):
    LATEST = "latest"
    FULL = "full"


class PostPaginationMode(Enum):
    ALL = "all"
    LAST_TWO = "last_two"
