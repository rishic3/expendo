import calendar
import pandas as pd
from typing import List, Union, Dict
from src.utils import get_credentials, get_latest_starting_month_idx
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

    def update_values(
        self,
        values: List[List[Union[str, float]]],
        range_name: str,
        value_input_option: str = "USER_ENTERED",
    ) -> None:
        """
        Update values in the spreadsheet.
        """
        try:
            service = self.service
            body = {"values": values}
            result = (
                service.spreadsheets()
                .values()
                .update(
                    spreadsheetId=self.spreadsheet_id,
                    range=range_name,
                    valueInputOption=value_input_option,
                    body=body,
                )
                .execute()
            )
            print(f"{(result.get('updatedCells'))} cells updated.")
            return
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

    def get_latest_col_index(self, col: str) -> str:
        """
        Get index of latest (vertically lowest) value in column.
        """
        try:
            col_result = self.get_column(col)
            assert col_result, f"No values found in {col}."
            return len(col_result)
        except HttpError as err:
            raise Exception(f"HTTP Error occurred: {err}")

    def add_monthly_stats(
        self,
        month: int,
        col_mapping: Dict[str, str],
        total_col: str,
    ) -> None:
        """
        Add monthly stats to spreadsheet.
        """
        try:
            date_col_df = pd.DataFrame(
                self.get_column(col_mapping.get("date")), columns=["Date"]
            )
            date_col_df = date_col_df[1:]  # index will be off by 1
            add_at_idx = get_latest_starting_month_idx(date_col_df, month, "Date") + 1
            print(f"Found month entries starting at index {add_at_idx}.")

            mo_range = f"{col_mapping.get('month')}:{col_mapping.get('month')}"
            cost_range = f"{col_mapping.get('cost')}:{col_mapping.get('cost')}"
            cat_range = f"{col_mapping.get('category')}:{col_mapping.get('category')}"

            month_name = calendar.month_name[month]
            sum_total_col = chr(ord(total_col) + 1)
            sum_total_range = (
                f"{sum_total_col}{add_at_idx}:{sum_total_col}{add_at_idx + 4}"
            )
            values = [
                [
                    "Groceries",
                    f'=SUMIFS({cost_range}, {mo_range}, "{month_name}", {cat_range}, {total_col}{add_at_idx})',
                ],
                [
                    "Meals",
                    f'=SUMIFS({cost_range}, {mo_range},  "{month_name}", {cat_range}, {total_col}{add_at_idx + 1})',
                ],
                [
                    "Other",
                    f'=SUMIFS({cost_range}, {mo_range},  "{month_name}", {cat_range}, {total_col}{add_at_idx + 2})',
                ],
                [
                    "Clothing",
                    f'=SUMIFS({cost_range}, {mo_range},  "{month_name}", {cat_range}, {total_col}{add_at_idx + 3})',
                ],
                [
                    "Relish",
                    f'=SUMIFS({cost_range}, {mo_range},  "{month_name}", {cat_range}, {total_col}{add_at_idx + 4})',
                ],
                ["Total", f"=SUM({sum_total_range})"],
            ]
            self.update_values(
                values, f"{total_col}{add_at_idx}:{sum_total_col}{add_at_idx + 5}"
            )

            return

        except HttpError as err:
            raise Exception(f"HTTP Error occurred: {err}")
