#!/usr/bin/env python3

import argparse
from check_device_report import read_report, get_command_json


def show_report_notes(report_file):
    """Show the report notes by querying report data."""
    try:
        # Read the JSON report file
        report_data = read_report(report_file)

        # Get report notes
        notes = report_data.get("notes", "")

        # Print the report notes
        print(notes)

    except Exception as e:
        print(f"ERROR: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Show report notes in the device report."
    )
    parser.add_argument(
        "--report",
        "-r",
        required=True,
        help="Path to the report JSON file (e.g., report.json)",
    )
    args = parser.parse_args()
    show_report_notes(args.report)
