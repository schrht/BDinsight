#!/usr/bin/env python3

import argparse
import json
import subprocess
import os


def read_report(report_file):
    """Read the JSON report file."""
    with open(report_file, "r") as f:
        return json.load(f)


def write_report(report_file, report_data):
    """Write the updated report data back to the JSON file."""
    with open(report_file, "w") as f:
        json.dump(report_data, f, indent=4)


def edit_report_notes(report_file):
    """Edit the report notes by calling a system editor."""
    try:
        # Read the JSON report file
        report_data = read_report(report_file)

        # Get report notes or initialize if not present
        notes = report_data.get("notes", "")

        # Create a temporary file to edit notes
        temp_file = ".temp_notes.txt"
        with open(temp_file, "w") as f:
            f.write(notes)

        # Open the system editor
        editor = os.getenv("EDITOR", "nano")  # Default to nano if no editor is set
        subprocess.run([editor, temp_file])

        # Read the updated notes from the temporary file
        with open(temp_file, "r") as f:
            updated_notes = f.read()

        # Update the notes in the report data
        if updated_notes != notes:
            report_data["notes"] = (
                updated_notes.strip()
            )  # Remove any surrounding whitespace

            # Write the updated report data back to the JSON file
            write_report(report_file, report_data)

            print("Report notes updated!")
        else:
            print("Report notes remained no change!")

        # Remove the temporary file
        os.remove(temp_file)

    except Exception as e:
        print(f"ERROR: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Edit report notes in the device report."
    )
    parser.add_argument(
        "--report",
        "-r",
        required=True,
        help="Path to the report JSON file (e.g., report.json)",
    )
    args = parser.parse_args()
    edit_report_notes(args.report)
