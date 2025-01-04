import pandas as pd
from typing import List
from src.utils import get_credentials
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build, Resource
from googleapiclient.errors import HttpError


class SpreadSheet:
    def __init__(self, spreadsheet_id: str):
        self.creds = get_credentials()
        self.spreadsheet_id = spreadsheet_id
        self._service = None

    @property
    def service(self) -> Resource:
        """
        Returns the service object.
        """
        if self._service is None:
            self._service = build("sheets", "v4", credentials=self.creds)
        return self._service

    def get_values(self, range_name: str) -> pd.DataFrame:
        """
        Return values in range from spreadsheet as a Pandas DF.
        """
        try:
            service = self.service
            result = (
                service.spreadsheets()
                .values()
                .get(spreadsheetId=self.spreadsheet_id, range=range_name)
                .execute()
            )
            rows = result.get("values", [])
            return pd.DataFrame(rows)
        except HttpError as err:
            raise Exception(f"HTTP Error occurred: {err}")

    def append_values(
        self,
        values_df: pd.DataFrame,
        range_name: str,
        value_input_option: str = "USER_ENTERED",
    ) -> dict:
        """
        Appends values to the spreadsheet.
        """
        try:
            service = self.service
            body = {"values": values_df.values.tolist()}
            result = (
                service.spreadsheets()
                .values()
                .append(
                    spreadsheetId=self.spreadsheet_id,
                    range=range_name,
                    valueInputOption=value_input_option,
                    body=body,
                )
                .execute()
            )
            print(f"{(result.get('updates').get('updatedCells'))} cells appended.")
            return result
        except HttpError as err:
            raise Exception(f"HTTP Error occurred: {err}")

    def get_last_populated_row(self, col: str) -> int:
        """
        Returns the last populated row in the specified column.
        """
        try:
            service = self.service
            col_range = f"{col}:{col}"
            result = (
                service.spreadsheets()
                .values()
                .get(spreadsheetId=self.spreadsheet_id, range=col_range)
                .execute()
            )
            rows = result.get("values", [])
            return len(rows)
        except HttpError as err:
            raise Exception(f"HTTP Error occurred: {err}")


if __name__ == "__main__":
    sid = "1NONAyZN-DU7VyRR4ystC8rDZ0aBQsEU65kTJiesV-c0"
    sheet = SpreadSheet(sid)
    out_pdf = sheet.get_values("K1:L7")
    print(out_pdf)
