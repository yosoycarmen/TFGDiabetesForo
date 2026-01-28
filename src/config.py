from enum import Enum
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"

class Config(Enum):
    forum_url = "https://diabetesforo.com/es/"
    forum_categories_url = "https://diabetesforo.com/es/categories/"
    raw_posts_file = str(DATA_DIR / "raw_posts.csv")
    raw_threads_file = str(DATA_DIR / "raw_threads.csv")
    raw_categories_file = str(DATA_DIR / "raw_categories.csv")

class ScrapingMode(Enum):
    LATEST = "latest"
    FULL = "full"


class PostPaginationMode(Enum):
    ALL = "all"
    LAST_TWO = "last_two"
