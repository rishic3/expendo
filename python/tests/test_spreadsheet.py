import pytest
import pandas as pd
from src.spreadsheet import SpreadSheet


@pytest.fixture
def sheet_id():
    """
    Test sheet:
    [['September', '', '9/25/24', '2.5', 'Nvidia cafe', 'Meals'],
     ['September', '', '9/25/24', '7.5', 'Nvidia cafe', 'Meals'],
     ['September', '', '9/26/24', '2.5', 'Nvidia cafe', 'Meals'],
     ['September', '', '9/26/24', '8.5', 'Nvidia cafe', 'Meals'],
     [],
     ['September', '', '9/27/24', '2.5', 'Nvidia cafe', 'Meals'],
     ['October', '', '10/27/24', '7.5', 'Nvidia cafe', 'Meals']]
    """

    return "1bex8CETqEtyGRb3TG-x3so5roUL7fFkZcqP5EfrkS0E"


def test_get_values(sheet_id: str) -> None:
    spreadsheet = SpreadSheet(sheet_id)
    values_df = pd.DataFrame(spreadsheet.get_values("A1:F2"))

    expected_df = pd.DataFrame(
        [
            ["September", "", "9/25/24", "2.5", "Nvidia cafe", "Meals"],
            ["September", "", "9/25/24", "7.5", "Nvidia cafe", "Meals"],
        ],
    )

    assert isinstance(values_df, pd.DataFrame)
    assert pd.DataFrame.equals(values_df, expected_df)

def test_get_column(sheet_id: str) -> None:
    spreadsheet = SpreadSheet(sheet_id)
    col_df = pd.DataFrame(spreadsheet.get_column("A"))
    expected_df = pd.DataFrame(
        [
            ["September"],
            ["September"],
            ["September"],
            ["September"],
            [],
            ["September"],
            ["October"],
        ],
    )
    assert pd.DataFrame.equals(col_df, expected_df)

def test_append_and_clear(sheet_id: str) -> None:
    spreadsheet = SpreadSheet(sheet_id)

    append_df = pd.DataFrame(
        [
            ["January", "", "10/26/24", "99.5", "Test location", "Groceries"],
            ["January", "", "10/26/24", "120.3", "Test location", "Groceries"],
        ],
    )

    spreadsheet.append_values(append_df.values.tolist(), "A:A")
    values_df = pd.DataFrame(spreadsheet.get_values("A8:F9"))
    assert pd.DataFrame.equals(append_df, values_df)

    # clear updates
    spreadsheet = SpreadSheet(sheet_id)
    spreadsheet.clear_values("A8:F9")
    values_df = pd.DataFrame(spreadsheet.get_values("A8:F9"))
    assert values_df.empty

def test_get_latest_col_value(sheet_id: str) -> None:
    spreadsheet = SpreadSheet(sheet_id)
    assert spreadsheet.get_latest_col_value("A") == "October"