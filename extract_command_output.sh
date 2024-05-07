#!/bin/bash

rptfile=$1
command_pattern=$2
search_pattern=$3
#rptfile=report_ST3500320AS_5QM1FBR6_20240502_163319.log

[[ -z $2 ]] && echo "Usage: $0 <report_file> <command_pattern> [search_pattern]" && exit 1

echo "INFO: searching report file '$rptfile'..." >&2
output=$(grep -n "^\$ .*${command_pattern}" "$rptfile")

# Locate the command and get the line number
if [[ $(echo "$output" | wc -l) = 0 ]]; then
    echo -e "ERROR: No commands were found!" >&2
    exit 1
elif [[ $(echo "$output" | wc -l) -gt 1 ]]; then
    echo -e "ERROR: Multiple commands were found, please update the command pattern you provided!" >&2
    echo -e "ERROR: Search Results:\n${output}" >&2
    exit 1
fi

cmd=$(echo "$output" | cut -d : -f 2-)
line=$(echo "$output" | cut -d : -f 1)

echo "INFO: found command '${cmd}' at line ${line}." >&2

# Locate the command output and get the line number range
start_line=$((line + 1))
output=$(grep -n '^----------------$' "$rptfile")
if ! echo "$output" | grep -q "^${start_line}:"; then
    echo "ERROR: Cannot locate the start line of the command output, please verify the format of the report file!" >&2
    exit 1
fi

end_line=$(echo "$output" | grep -A 1 "^${start_line}:" | tail -n 1 | cut -d : -f 1)
if [[ -z $end_line ]]; then
    echo "ERROR: Cannot locate the end line of the command output, please verify the format of the report file!" >&2
    exit 1
fi

echo "INFO: found command output from line ${start_line} to ${end_line}." >&2

# Get the command output
command_output=$(sed -n "${start_line},${end_line}p" "$rptfile")

# Print the entire command output or the matched content if a search pattern is provided
if [[ -z $search_pattern ]]; then
    echo "$command_output" | grep -v '^----------------$'
else
    echo "$command_output" | grep -v '^----------------$' | grep "$search_pattern"
fi

exit 0
