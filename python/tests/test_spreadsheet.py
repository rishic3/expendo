import pytest
import pandas as pd
from src.spreadsheet import SpreadSheet

@pytest.fixture
def test_sheet_id():
    return "1bex8CETqEtyGRb3TG-x3so5roUL7fFkZcqP5EfrkS0E"


def test_get_values(test_sheet_id: str) -> None:
    spreadsheet = SpreadSheet(test_sheet_id)
    values_df = spreadsheet.get_values("A1:F2")

    expected_df = pd.DataFrame(
        [
            ["September", "", "9/25/24", "2.5", "Nvidia cafe", "Meals"],
            ["September", "", "9/25/24", "7.5", "Nvidia cafe", "Meals"],
        ],
    )

    assert isinstance(values_df, pd.DataFrame)
    assert pd.DataFrame.equals(values_df, expected_df)

def test_get_last_populated_row(test_sheet_id: str) -> None:
    spreadsheet = SpreadSheet(test_sheet_id)
    last_row = spreadsheet.get_last_populated_row("A")

    assert last_row == 7


def test_append_values(test_sheet_id: str) -> None:
    spreadsheet = SpreadSheet(test_sheet_id)

    append_df = pd.DataFrame(
        [
            ["January", "", "10/26/24", "99.5", "Test location", "Groceries"],
            ["January", "", "10/26/24", "120.3", "Test location", "Groceries"],
        ],
    )

    result = spreadsheet.append_values(append_df, "A:A")

    print(result)


    # values_df = spreadsheet.get_values("A1:F2")

    # expected_df = pd.DataFrame(
    #     [
    #         ["September", "", "9/25/24", "2.5", "Nvidia cafe", "Meals"],
    #         ["September", "", "9/25/24", "7.5", "Nvidia cafe", "Meals"],
    #     ],
    # )

    # assert isinstance(values_df, pd.DataFrame)
    # assert pd.DataFrame.equals(values_df, expected_df)
