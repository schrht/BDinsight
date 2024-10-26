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


def get_git_version():
    try:
        # Run the git command to get the current commit version
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
            cwd=".",  # Change to the root directory of the script
        )
        return (
            result.stdout.decode().strip()
        )  # Decode the output and remove any surrounding whitespace
    except subprocess.CalledProcessError:
        return "Unknown"  # Return 'Unknown' if the command fails


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


def get_device_info(device, device_type="auto"):
    cmd = f"sudo smartctl --json -i {device} -d {device_type}"
    info, _, returncode, _ = run_command(cmd)

    if returncode != 0 or not is_json(info):
        print(f"ERROR: unable to get device information: '{cmd}' failed.")
        exit(1)

    info = json.loads(info)
    device_info = {
        "model": info.get("model_name", "Unknown"),
        "serial_number": info.get("serial_number", "Unknown"),
    }

    return device_info


def main(device, device_type="auto", output_file="report.json"):
    check_block_device(device)

    # Get device information
    device_info = get_device_info(device, device_type)

    report_data = {
        "script_name": "generate_device_report.py",
        "git_version": get_git_version(),
        "generated_on": datetime.datetime.now().isoformat(),
        "device": device_info,
        "commands": [],
    }

    # Define commands to include in the report
    commands = [
        "uname -a",
        "smartctl --version",
        "fdisk --version",
        "lsblk --version",
        "sudo smartctl -i --json=o {device} -d {device_type}",
        "sudo smartctl -a --json=o {device} -d {device_type}",
        "sudo smartctl -x --json=o {device} -d {device_type}",
        "sudo smartctl -q errorsonly -A -H -l selftest -l error --json=o {device} -d {device_type}",
        "sudo fdisk -l {device}",
        "lsblk -p {device}",
    ]
    parameters = {"device": device, "device_type": device_type}

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

        if returncode != 0:
            print(f"WARNING: '{cmd}' returns '{returncode}'.")

        # Check if the output is JSON and insert it into the command data
        if is_json(stdout):
            command_data["json_output"] = json.loads(stdout)

        report_data["commands"].append(command_data)

    # Write the report data to the output file in JSON format
    with open(output_file, "w") as rpt:
        json.dump(report_data, rpt, indent=4)

    print(f"INFO: Report generated: {output_file}")


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
        "--device-type",
        "-t",
        required=False,
        default="auto",
        help="Type of the block device (e.g., auto, sat, nvme, ...)",
    )
    parser.add_argument(
        "--output",
        "-o",
        required=False,
        default="report.json",
        help="Output file name for the report (e.g., report.json)",
    )
    args = parser.parse_args()
    main(args.device, args.device_type, args.output)
