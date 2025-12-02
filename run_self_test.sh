#!/bin/bash

# Description:
#   Trigger the Block Device self-test.
# Maintainer:
#   Charles Shi <schrht@gmail.com>

show_usage() {
	echo "Usage:   ${BASH_SOURCE[0]} <block_device> [short|long]"
	echo "Example: ${BASH_SOURCE[0]} /dev/sdx short"
}

[[ -z $1 ]] && show_usage && exit 1
if [[ -b $1 ]]; then
	dev=$1
else
	echo "$1 is not a block device!"
	exit 1
fi

[[ -n $2 ]] && type=$2 || type=short

# Trigger the self-test
if sudo smartctl -t "$type" "$dev" -d sat; then
	echo -e "\nThe self-test for '$dev' has been triggered."
	echo -e "Run 'sudo smartctl -l selftest ${dev}' to get the report by then."
	watch -c -d -b -e -n 5 sudo smartctl -l selftest "${dev}" -d sat
	exit 0
else
	echo -e "\nFail to trigger the self-test."
	exit 1
fi

