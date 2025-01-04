import calendar
import argparse
import pandas as pd
from src.spreadsheet import SpreadSheet
from src.classifier import *


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="expendo", description="Process, categorize, and track your expenses."
    )
    parser.add_argument("path", type=str, help="Path to new transactions CSV.")
    parser.add_argument("sheet_id", type=str, help="Google Sheet ID to update.")
    parser.add_argument(
        "col_mappings",
        type=dict,
        help="Mapping of (column, column_letter) for month, date, cost, description, and category. For monthly stats, also include totals.",
    )
    parser.add_argument(
        "threshold",
        type=float,
        default=0.75,
        help="Threshold for similarity classification.",
    )
    parser.add_argument(
        "monthly_stats",
        type=int,
        default=None,
        help="Optional: month for which to add monthly stats to the sheet.",
    )

    args = parser.parse_args()
    col_mappings = args.col_mappings

    # Load data
    sheet = SpreadSheet(args.sheet_id)
    new_data = load_and_process_transactions(args.path)
    old_data = load_and_process_spreadsheet(sheet, args.col_mappings)

    # Remove overlapping data
    latest_date = sheet.get_latest_col_value(col_mappings.get("date"))
    new_data = new_data[new_data["Date"] >= latest_date]
    new_data.rename(columns={"Name": "description"}, inplace=True)

    # Embed and classify
    new_data_labeled, low_conf = embed_and_classify(
        old_data, new_data, "description", "category", args.threshold
    )
    for (index, similarity), (name, label) in low_conf.items():
        print(
            f"Item '{name}' at index {index} has low confidence ({similarity}); best match was {label}."
        )

    # Reorder and format
    new_data_labeled["month"] = pd.to_datetime(new_data_labeled["Date"]).dt.month.apply(
        lambda x: calendar.month_name[x]
    )
    cols = ["month", "Date", "Amount", "description", "category"]
    new_data_labeled = new_data_labeled[cols]
    new_data_labeled.insert(1, "blank", "")

    # Append to sheet
    mo = col_mappings.get("month")
    cat = col_mappings.get("category")

    next_idx = sheet.get_latest_col_index(mo) + 2
    append_range = f"{mo}{next_idx}:{cat}{next_idx}"
    sheet.append_values(new_data_labeled.values.tolist(), append_range)

    # Add monthly stats
    if args.monthly_stats:
        sheet.add_monthly_stats(
            args.monthly_stats, col_mappings, col_mappings.get("total")
        )
