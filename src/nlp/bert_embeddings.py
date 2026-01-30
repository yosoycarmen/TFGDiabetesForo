from src.config import Config
import pandas as pd

csv_path = Config.clean_posts_file.value
df = pd.read_csv(csv_path)


texts = (
    df["content_clean_nostop"]
    .fillna("")
    .astype(str)
)

mask = texts.str.len() >= 10
df = df[mask].copy()
texts = texts[mask].tolist()

len(df), df["content_clean_basic"].head()