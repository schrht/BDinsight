#!/usr/bin/env python3

import json
import argparse
import sys


def read_report(report_file):
    with open(report_file, "r") as f:
        return json.load(f)


def get_command_json(data, command):
    """Retrieve the JSON block for the specified command line from the report."""
    for block in data.get("commands", []):
        if command in block["command"]:
            return block
    return {}


def check_smart_status(data):
    if "smart_status" in data and "passed" in data["smart_status"]:
        return data["smart_status"]["passed"]
    return None


def sat_checkpoints(data):
    """Perform SAT checkpoints based on SMART data."""
    failures = []

    json_output = get_command_json(data, "sudo smartctl -a --json=o {device}").get(
        "json_output", {}
    )

    # Check Reallocated_Sector_Ct
    reallocated = None
    for attr in json_output.get("ata_smart_attributes", {}).get("table", []):
        if attr["name"] == "Reallocated_Sector_Ct":
            reallocated = attr["raw"]["value"]
            if reallocated > 0:
                failures.append(
                    f"Reallocated_Sector_Ct checkpoint failed: Value ({reallocated}) is greater than 0."
                )
            break
    if reallocated is None:
        failures.append("WARN: Reallocated_Sector_Ct not found.")

    # Check Current_Pending_Sector
    pending = None
    for attr in data.get("ata_smart_attributes", {}).get("table", []):
        if attr["name"] == "Current_Pending_Sector":
            pending = attr["raw"]["value"]
            if pending > 0:
                failures.append(
                    f"Current_Pending_Sector checkpoint failed: Value ({pending}) is greater than 0."
                )
            break
    if pending is None:
        failures.append("WARN: Current_Pending_Sector not found.")

    return failures


def nvme_checkpoints(data):
    # Placeholder for NVMe checkpoint checks
    print("NVMe checkpoint checks not implemented yet.")
    return []


def common_checkpoints(data):
    """Check common checkpoints."""
    failures = []

    # Check return code from the self-test command
    smartctl_all_return_code = get_command_json(
        data, "sudo smartctl -a --json=o {device}"
    ).get("return_code")

    if smartctl_all_return_code is None:
        print("WARN: unable to get the return code of smartctl-all command.")
    elif smartctl_all_return_code != 0:
        failures.append("smartctl-all command return code is not zero.")

    smartctl_error_return_code = get_command_json(
        data, "sudo smartctl -q errorsonly -A -H -l selftest -l error --json=o {device}"
    ).get("return_code")

    if smartctl_error_return_code is None:
        print("WARN: unable to get the return code of smartctl-error command.")
    elif smartctl_error_return_code != 0:
        failures.append("smartctl-error command return code is not zero.")

    return failures


def perform_checkpoints(data):
    device_type = (
        get_command_json(data, "sudo smartctl -a --json=o {device}")
        .get("json_output", {})
        .get("device", {})
        .get("type", "unknown")
    )
    overall_status = "PASS"
    overall_failures = []

    if device_type == "sat":
        overall_failures.extend(sat_checkpoints(data))
    elif device_type == "nvme":
        overall_failures.extend(nvme_checkpoints(data))
    else:
        print(f"ERROR: Device type '{device_type}' not supported.")
        return 1  # Return code for unsupported device types

    overall_failures.extend(common_checkpoints(data))

    if overall_failures:
        overall_status = "FAIL"
        print(f"Overall Status: {overall_status}")
        for failure in overall_failures:
            print(f"  - {failure}")
        return len(overall_failures)

    print("Overall Status: PASS")
    return 0


def main(report_file):
    try:
        data = read_report(report_file)
        return perform_checkpoints(data)
    except Exception as e:
        print(f"ERROR: {e}")
        return 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Check device report for SMART status."
    )
    parser.add_argument(
        "--report", "-r", required=True, help="JSON report file to analyze"
    )
    args = parser.parse_args()
    exit_code = main(args.report)
    sys.exit(exit_code)
