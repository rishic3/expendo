from typing import Dict, Tuple
import numpy as np
import pandas as pd
from src.spreadsheet import SpreadSheet
from sentence_transformers import SentenceTransformer, util


def load_and_process_transactions(path: str) -> pd.DataFrame:
    """
    Load new transactions data from CSV, drop unneeded cols and rows already in sheet.
    """
    pdf = pd.read_csv(path).drop(columns=["Memo", "Transaction"], axis=1)
    pdf["Amount"] = pdf["Amount"] * -1
    pdf = pdf[pdf["Amount"] > 0]

    return pdf


def load_and_process_spreadsheet(
    sheet: SpreadSheet, col_mappings: Dict[str, str]
) -> pd.DataFrame:
    """
    Load old transactions data from Google Sheets, preprocess and drop unneeded cols.
    """
    dates = sheet.get_column(col_mappings.get("date"))
    descriptions = sheet.get_column(col_mappings.get("description"))
    categories = sheet.get_column(col_mappings.get("category"))

    pdf = pd.DataFrame(
        {"date": dates, "description": descriptions, "category": categories}
    )
    pdf = pdf[1:].dropna()
    pdf = pdf.map(lambda x: x[0] if x else None)

    return pdf


def embed_and_classify(
    old_data: pd.DataFrame,
    new_data: pd.DataFrame,
    feature_col: str,
    label_col: str,
    threshold: float,
) -> Tuple[pd.DataFrame, Dict[int, str]]:
    """
    Embed and classify transactions data, returning new data with labels and low similarity features that need manual labels.
    """
    model = SentenceTransformer("all-MiniLM-L6-v2")
    old_names = old_data[feature_col].tolist()
    new_names = new_data[feature_col].tolist()

    new_embeddings = model.encode(new_names, convert_to_tensor=True)
    old_embeddings = model.encode(old_names, convert_to_tensor=True)

    similarity_matrix = (
        util.pytorch_cos_sim(new_embeddings, old_embeddings).cpu().numpy()
    )

    labels = []
    low_conf = {}
    for i, similarities in enumerate(similarity_matrix):
        max_similarity = np.max(similarities)
        if max_similarity >= threshold:
            best_match_index = np.argmax(similarities)
            labels.append(old_data.iloc[best_match_index][label_col])
        else:
            labels.append(None)
            low_conf[i] = new_data.iloc[i][feature_col]

    new_data[label_col] = labels

    return new_data, low_conf
