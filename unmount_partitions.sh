#!/bin/bash

# Description:
#   Unmount partitions for the Block Device.
# Maintainer:
#   Charles Shi <schrht@gmail.com>

show_usage() {
	script_name=$(basename "${BASH_SOURCE[0]}")
	echo "Unmount partitions for the Block Device."
	echo "Usage:   $script_name <block_device>"
	echo "Example: $script_name /dev/sdx"
}

# Display usage if no block device is provided
[[ -z $1 ]] && show_usage && exit 1

# Check if the provided argument is a block device
if [[ -b $1 ]]; then
	dev=$1
else
	echo "$1 is not a block device!"
	exit 1
fi

# Query mounted partitions
echo "Querying mount points for '$dev' ..."
mountpoints=$(lsblk --output MOUNTPOINT "$dev" | grep '/')
if [[ -n "$mountpoints" ]]; then
	echo "The following partition(s) are currently mounted:"
	for mp in $mountpoints; do echo "- $mp"; done
	echo
else
	echo "No partitions are mounted to the system."
	exit 0
fi

# Unmount partitions
for mp in $mountpoints; do
	echo "Unmounting '$mp'..."
	if ! sudo umount "$mp"; then
		echo "Error: Failed to unmount '$mp'."
		exit 1
	fi
done

# Verify unmounting
echo -e "\nVerifying mount points for '$dev' ..."
if lsblk --output MOUNTPOINT "$dev" | grep -q '/'; then
	echo "Error: Some partitions are still mounted to the system."
	exit 1
else
	echo "No partitions are mounted to the system anymore."
	exit 0
fi
