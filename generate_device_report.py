#!/usr/bin/env python3

import argparse
import subprocess
import os
import re
import datetime
import json
import time
import stat

# Description:
#   Generate a detailed report for the block device using smartctl and other commands.
# Maintainer:
#   Charles Shi <schrht@gmail.com>


def show_usage():
    print("Generate a detailed report for the block device.")
    print(
        "Usage:   generate_device_report.py --device <block_device> --output <output_file>"
    )
    print("Example: generate_device_report.py --device /dev/sdx --output report.json")


def check_block_device(device):
    if not os.path.exists(device):
        print(f"{device} does not exist!")
        exit(1)
    if not stat.S_ISBLK(os.stat(device).st_mode):
        print(f"{device} is not a block device!")
        exit(1)


def run_command(command):
    """Run a shell command and return its output."""
    try:
        start_time = time.time()
        result = subprocess.run(
            command,
            shell=True,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        end_time = time.time()
        time_used = end_time - start_time
        return (
            result.stdout.decode(),
            result.stderr.decode(),
            result.returncode,
            time_used,
        )
    except subprocess.CalledProcessError as e:
        end_time = time.time()
        time_used = end_time - start_time
        return e.stdout.decode(), e.stderr.decode(), e.returncode, time_used


def is_json(output):
    """Check if the output is a valid JSON."""
    try:
        json.loads(output)
        return True
    except json.JSONDecodeError:
        return False


def get_device_info(device):
    output, _, _, _ = run_command(f"sudo smartctl -i {device}")
    return output


def parse_device_info(info):
    model = re.search(r"Device Model:\s*(.*)", info)
    serial_number = re.search(r"Serial Number:\s*(.*)", info)
    return model.group(1).strip() if model else "Unknown", (
        serial_number.group(1).strip() if serial_number else "Unknown"
    )


def main(device, output_file):
    check_block_device(device)

    # Get device information
    device_info = get_device_info(device)

    # Parse device information
    model, serial_number = parse_device_info(device_info)

    report_data = {
        "script_name": "generate_device_report.py",
        "generated_on": datetime.datetime.now().isoformat(),
        "device": {"model": model, "serial_number": serial_number},
        "commands": [],
    }

    # Define commands to include in the report
    commands = [
        "uname -a",
        "smartctl --version",
        "fdisk --version",
        "lsblk --version",
        "sudo smartctl -a --json=o {device}",
        "sudo smartctl -x --json=o {device}",
        "sudo smartctl -q errorsonly -A -H -l selftest -l error --json=o {device}",
        "sudo fdisk -l {device}",
        "lsblk -p {device}",
    ]
    parameters = {"device": device}

    # Iterate over the list of commands and execute them
    for cmd in commands:
        stdout, stderr, returncode, time_used = run_command(cmd.format(**parameters))

        command_data = {
            "command": cmd,
            "command_line": cmd.format(**parameters),
            "stdout": stdout.strip(),
            "stderr": stderr.strip(),
            "return_code": returncode,
            "time_used": time_used,
        }

        # Check if the output is JSON and insert it into the command data
        if is_json(stdout):
            command_data["json_output"] = json.loads(stdout)

        report_data["commands"].append(command_data)

    # Write the report data to the output file in JSON format
    with open(output_file, "w") as rpt:
        json.dump(report_data, rpt, indent=4)

    print(f"Report generated: {output_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate a detailed report for the block device."
    )
    parser.add_argument(
        "--device",
        "-d",
        required=True,
        help="Path to the block device (e.g., /dev/sdx)",
    )
    parser.add_argument(
        "--output",
        "-o",
        required=True,
        help="Output file name for the report (e.g., report.json)",
    )
    args = parser.parse_args()
    main(args.device, args.output)
