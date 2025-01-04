from typing import List, Union
from src.utils import get_credentials
from googleapiclient.discovery import build, Resource
from googleapiclient.errors import HttpError

class SpreadSheet:
    """
    SpreadSheet class to interact w/Google Sheets API.
    """

    def __init__(self, spreadsheet_id: str):
        self.creds = get_credentials()
        self.spreadsheet_id = spreadsheet_id
        self._service = None

    @property
    def service(self) -> Resource:
        """
        Build and return the service object.
        """
        if self._service is None:
            self._service = build("sheets", "v4", credentials=self.creds)
        return self._service

    def get_values(self, range_name: str) -> List[List[Union[str, float]]]:
        """
        Return values in range from spreadsheet.
        """
        try:
            service = self.service
            result = (
                service.spreadsheets()
                .values()
                .get(spreadsheetId=self.spreadsheet_id, range=range_name)
                .execute()
            )
            return result.get("values", [])
        except HttpError as err:
            raise Exception(f"HTTP Error occurred: {err}")

    def get_column(self, col: str) -> List[List[str]]:
        """
        Return values in column from spreadsheet.
        """
        try:
            range = f"{col}:{col}"
            result = self.get_values(range)
            return result
        except HttpError as err:
            raise Exception(f"HTTP Error occurred: {err}")

    def append_values(
        self,
        values: List[List[Union[str, float]]],
        range_name: str,
        value_input_option: str = "USER_ENTERED",
    ) -> None:
        """
        Appends values to the spreadsheet.
        """
        try:
            service = self.service
            body = {"values": values}
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
            return
        except HttpError as err:
            raise Exception(f"HTTP Error occurred: {err}")

    def clear_values(self, range_name: str) -> None:
        """
        Clear values in range from spreadsheet.
        """
        try:
            service = self.service
            result = (
                service.spreadsheets()
                .values()
                .clear(spreadsheetId=self.spreadsheet_id, range=range_name)
                .execute()
            )
            print(f"Cleared range {result.get('clearedRange').split('!')[1]}.")
            return
        except HttpError as err:
            raise Exception(f"HTTP Error occurred: {err}")

    def get_latest_col_value(self, col: str) -> str:
        """
        Get latest (vertically lowest) value in column.
        """
        try:
            col_result = self.get_column(col)
            assert col_result, f"No values found in {col}."
            return col_result[-1][0]
        except HttpError as err:
            raise Exception(f"HTTP Error occurred: {err}")

    def compute_monthly_stats(self, month: str) -> None:
        # TODO
        return