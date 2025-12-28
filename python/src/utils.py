import os
import pandas as pd
from typing import List, Optional, Tuple
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


def get_month_range(
    date_col_df: pd.DataFrame, month: int, date_col: str, year: Optional[int] = None
) -> Tuple[int, int]:
    """
    Get the start and end indices of a month block in the dataframe.

    Args:
        date_col_df: DataFrame containing the date column
        month: Month number (1-12)
        date_col: Name of the date column
        year: Optional year to filter by. If None, uses the latest instance of the month.

    Returns:
        Tuple of (start_idx, end_idx) for the month block (0-based df indices)
    """
    date_col_df = date_col_df.copy()
    date_col_df[date_col] = pd.to_datetime(date_col_df[date_col])

    # Filter by month (and optionally year)
    mask = date_col_df[date_col].dt.month == month
    if year is not None:
        mask &= date_col_df[date_col].dt.year == year

    indices_of_month = date_col_df[mask].index
    if len(indices_of_month) == 0:
        raise ValueError(f"No entries found for month {month}" + (f" year {year}" if year else ""))

    # Find the contiguous block containing the last matching index
    last_index = indices_of_month[-1]
    first_index = indices_of_month[0]

    # If year is specified, we have exact matches - find the contiguous block
    # If no year, find the latest contiguous block of this month
    if year is not None:
        # Find start of contiguous block from first matching index
        start_idx = first_index
        end_idx = last_index
    else:
        # Original behavior: find the latest instance of the month
        start_idx = last_index
        for idx in range(last_index, -1, -1):
            if pd.isna(date_col_df.loc[idx, date_col]):
                continue
            if date_col_df.loc[idx, date_col].month != month:
                start_idx = idx + 1
                break
            start_idx = idx
        end_idx = last_index

    return (start_idx, end_idx)
