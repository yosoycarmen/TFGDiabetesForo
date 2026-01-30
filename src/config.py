from enum import Enum
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]

DATA_DIR_RAW = BASE_DIR / "data" / "raw"
DATA_DIR_MODELS = BASE_DIR / "models"
DATA_DIR_CLEAN = BASE_DIR / "data" / "processed"

class Config(Enum):
    forum_url = "https://diabetesforo.com/es/"
    forum_categories_url = "https://diabetesforo.com/es/categories/"
    raw_posts_file = str(DATA_DIR_RAW / "raw_posts.csv")
    raw_threads_file = str(DATA_DIR_RAW / "raw_threads.csv")
    raw_categories_file = str(DATA_DIR_RAW / "raw_categories.csv")

    clean_posts_file = str(DATA_DIR_CLEAN / "processed_posts.csv")
    dictionary_path = str(DATA_DIR_MODELS / "dictionary.dict")

    embeddings_path = str(DATA_DIR_MODELS / "sbert_embeddings.npy")
    embeddings2_path = str(DATA_DIR_MODELS / "2sbert_embeddings.npy")

class ScrapingMode(Enum):
    LATEST = "latest"
    FULL = "full"


class PostPaginationMode(Enum):
    ALL = "all"
    LAST_TWO = "last_two"
