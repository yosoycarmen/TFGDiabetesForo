from pathlib import Path
import pandas as pd
import re

from src.config import Config

# OJO: tu regex ya estaba bien para "solo símbolos/puntuación"
regex = r'[\\"\\#\\$\\%\\&\\\'\\(\\)\\*\\+\\,\\-\\.\\/\\:\\;\\<\\=\\>\\?\\[\\\\\\]\\^_\\`\\{\\|\\}\\~]'

class DataCleaner:
    def clean_dataset(self) -> pd.DataFrame:
        path = Path(Config.raw_posts_file.value)

        df = pd.read_csv(path, encoding="utf-8", on_bad_lines="skip")

        if "content" not in df.columns:
            raise ValueError("El CSV no tiene columna 'content'.")

        # Crea/actualiza la columna limpia
        df["content_clean_basic"] = df["content"].astype(str).map(self.basic_clean)

        # Sobrescribe el MISMO CSV
        df.to_csv(path, index=False, encoding="utf-8")
        print(f"✅ CSV actualizado (sobrescrito) en: {path}")

        return df

    def basic_clean(self, text: str) -> str:
        # Solo regex -> sustituye signos por espacios y normaliza espacios
        text = re.sub(regex, " ", text)
        text = re.sub(r"\s+", " ", text).strip()
        return text
