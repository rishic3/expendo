import os
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

    # get abs paths
    token_path = os.path.join(os.path.dirname(__file__), "auth/token.json")
    creds_path = os.path.join(os.path.dirname(__file__), "auth/credentials.json")

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
