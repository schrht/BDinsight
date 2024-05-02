#!/bin/bash

# Description:
#   Unmount partitions for the Block Device.
# Maintainer:
#   Charles Shi <schrht@gmail.com>

show_usage()
{
	echo "Usage:   $0 <block_device>"
	echo "Example: $0 /dev/sdx"
}

[[ -z $1 ]] && show_usage && exit 1
[[ -b $1 ]] && dev=$1 || { echo "$1 is not a block device!"; exit 1; }

# Query mounted partitions
echo "Querying mount points for '$dev' ..."
mountpoints=$(lsblk --output MOUNTPOINTS $dev | grep '/')
if [[ -n "$mountpoints" ]]; then
	for mp in $mountpoints; do echo $mp; done
	echo
else
	echo "No partitions are mounted to the system."
	exit 0
fi

for mp in $mountpoints; do
	echo "Unmounting '$mp'..."
	sudo umount $mp
done

echo -e "\nVerifying mount points for '$dev' ..."
if (lsblk --output MOUNTPOINTS $dev | grep '/'); then
	echo "Some partitions are still mounted to the system."
	exit 1
else
	echo "No partitions are mounted to the system anymore."
	exit 0
fi

