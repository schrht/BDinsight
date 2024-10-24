#!/usr/bin/env python3

import json
import argparse
import re
from datetime import datetime


def read_report(report_file):
    """Read the report JSON file."""
    with open(report_file, "r") as f:
        return json.load(f)


def generate_filename(report_data):
    """Generate the suggested filename based on the report data."""
    device_model = re.sub(
        r"[^a-zA-Z0-9]",
        "-",
        report_data.get("device", {}).get("model", "unknown_model"),
    )
    serial_number = re.sub(
        r"[^a-zA-Z0-9]",
        "-",
        report_data.get("device", {}).get("serial_number", "unknown_serial"),
    )

    # Get timestamp from generated_on
    generated_on = report_data.get(
        "generated_on", "1970-01-01T00:00:00"
    )  # Default to a base timestamp if missing
    timestamp = datetime.fromisoformat(generated_on).strftime("%y%m%d-%H%M%S")

    # Create the suggested filename
    suggested_filename = (
        f"device_report_{device_model}_{serial_number}_{timestamp}.json"
    )
    return suggested_filename


def main(report_file):
    try:
        report_data = read_report(report_file)
        suggested_filename = generate_filename(report_data)
        print(f"Suggested Filename: {suggested_filename}")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate a suggested filename from report.json."
    )
    parser.add_argument(
        "--report",
        "-r",
        required=True,
        help="Path to the report JSON file (e.g., report.json)",
    )
    args = parser.parse_args()
    main(args.report)
