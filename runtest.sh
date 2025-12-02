#!/bin/bash

if [[ -z $2 ]]; then
	echo "Usage: $0 <device> <device-type> [message]"
	exit 1
fi

message="${3:-'Red Hat e-Waste 2024'}"

echo "Generating device report..."
./generate_device_report.py --device $1 --device-type $2 --output report.json || exit 1

echo -e "\nChecking device report..."
./show_device_info.py --report report.json
./check_device_report.py --report report.json

echo -e "\nAdd notes to the report..."
./edit_report_notes.py --report report.json --message "$message"
./show_report_notes.py --report report.json

echo -e "\nRenaming report file..."
output=$(./suggest_report_filename.py --report report.json)
filename=$(echo $output | awk -F ':' '{print $2}' | tr -d ' ')
mv -i report.json $filename && echo "Report renamed: $filename"

exit 0
