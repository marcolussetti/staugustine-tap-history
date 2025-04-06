import sys
import json
import csv
from pathlib import Path
from datetime import datetime
import pytz  # Import the pytz library


def append_to_yearly_files(new_json, yearly_json, yearly_csv):
    """Append data from new_json to yearly_json and yearly_csv in Vancouver time."""

    try:
        # JSON is already sorted by jq
        with open(new_json, "r") as f:
            new_data = json.load(f)

        # Get the current date in Vancouver time in ISO format
        vancouver_tz = pytz.timezone("America/Vancouver")
        current_date = datetime.now(vancouver_tz).isoformat()

        # Add the current date to each new data entry
        dated_new_data = []
        for item in new_data:
            item["date"] = current_date
            dated_new_data.append(item)

        # JSON
        # Load existing yearly JSON data or initialize an empty list
        if Path(yearly_json).exists():
            with open(yearly_json, "r") as f:
                yearly_data = json.load(f)
        else:
            yearly_data = []

        # Combine and write to the yearly JSON file (no sorting needed)
        combined_json_data = yearly_data + dated_new_data
        with open(yearly_json, "w") as f:
            json.dump(combined_json_data, f, indent=2)

        # CSV
        # Prepare CSV data from the new data
        if dated_new_data:  # Only proceed if there's data to write
            keys = list(dated_new_data[0].keys())  # use existing headers
            # Force date at the top
            if keys[0] != "date":
                keys.insert(0, "date")

            csv_data = [keys] + [
                [item.get("date", current_date)] + [item.get(k, "") for k in keys[1:]]
                for item in dated_new_data
            ]

            # Load existing yearly CSV data or create header
            if Path(yearly_csv).exists():

                with open(yearly_csv, "r") as f:
                    reader = csv.reader(f)
                    yearly_csv_data = list(reader)
                header = yearly_csv_data[0]  # Grab the existing header

                if header[0] != "date":
                    print(
                        f"Yearly csv had a column that did not start with date. Please correct",
                        file=sys.stderr,
                    )
                    sys.exit(1)
                # Concatenate the two results to be the combination if it exists
                yearly_rows = yearly_csv_data[1:]

                combined_csv_data = csv_data[1:] + yearly_rows

            else:
                combined_csv_data = csv_data[1:]
                header = csv_data[0]

            with open(yearly_csv, "w", newline="") as f:
                writer = csv.writer(f)

                writer.writerow(header)  # Ensure the header
                writer.writerows(combined_csv_data)

    except Exception as e:
        print(f"Error processing files: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print(
            "Usage: python3 yearly_files.py <new_json> <yearly_json> <yearly_csv>",
            file=sys.stderr,
        )
        sys.exit(1)

    new_json, yearly_json, yearly_csv = sys.argv[1:4]
    append_to_yearly_files(new_json, yearly_json, yearly_csv)
