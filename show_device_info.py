#!/usr/bin/env python3

import argparse
from check_device_report import read_report, get_command_json


def show_device_info(report_file):
    """Show the device info by querying report data."""
    try:
        # Read the JSON report file
        report_data = read_report(report_file)

        # Get device info
        command_json = get_command_json(
            report_data, "sudo smartctl -i --json=o {device}"
        )
        device_info = (
            command_json.get("json_output", {}).get("smartctl", {}).get("output", [])
        )

        # Print the device info
        for line in device_info:
            print(line)

    except Exception as e:
        print(f"ERROR: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Show device info in the device report."
    )
    parser.add_argument(
        "--report",
        "-r",
        required=True,
        help="Path to the report JSON file (e.g., report.json)",
    )
    args = parser.parse_args()
    show_device_info(args.report)
