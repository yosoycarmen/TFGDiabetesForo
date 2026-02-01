from src.config import Config
import pandas as pd

class BertEmbeddings:
    def __init__(self):
        self.csv_path = Config.clean_posts_file.value
        self.df = pd.read_csv(self.csv_path)

        self.texts = (
            self.df["content"]
            .fillna("")
            .astype(str)
        )

    def empty_filter(self):
        mask = self.texts.str.len() >= 10
        df = self.df[mask].copy()
        texts = self.texts[mask].tolist()

