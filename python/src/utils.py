import os
import pandas as pd
from typing import List
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow


def get_credentials(
    SCOPES: List[str] = ["https://www.googleapis.com/auth/spreadsheets"],
) -> Credentials:
    """
    Accesses tokens in token.json, refreshes/stores new tokens via web login if necessary.
    """
    creds = None

    # get abs paths from parent dir
    token_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "auth/token.json")
    creds_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "auth/credentials.json")

    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        elif os.path.exists(creds_path):
            flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
            creds = flow.run_local_server(port=0)
        else:
            raise ValueError("auth/credentials.json not found.")

        with open(token_path, "w") as token:
            token.write(creds.to_json())

    return creds


def get_latest_starting_month_idx(
    date_col_df: pd.DataFrame, month: int, date_col: str
) -> int:
    """
    Get the index of the first date in the latest instance of the given month.
    """
    date_col_df[date_col] = pd.to_datetime(date_col_df[date_col])
    dates_months = date_col_df[date_col].dt.month
    indices_of_month = dates_months[dates_months == month].index

    last_index = indices_of_month[-1]
    for idx in range(
        last_index, -1, -1
    ):  # Iterate backward to find the first in the block
        if (
            pd.isna(date_col_df.loc[idx, date_col])
            or date_col_df.loc[idx, date_col].month == month
        ):
            continue
        return idx + 1

    raise ValueError("No valid index found.")
