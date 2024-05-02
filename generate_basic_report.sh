#!/bin/bash

# Description:
#   Generate Basic Report for the Block Device.
# Maintainer:
#   Charles Shi <schrht@gmail.com>

show_usage() {
	echo "Usage:   $0 <block_device>"
	echo "Example: $0 /dev/sdx"
}

[[ -z $1 ]] && show_usage && exit 1
[[ -b $1 ]] && dev=$1 || {
	echo "$1 is not a block device!"
	exit 1
}

# Install software
type smartctl &>/dev/null || sudo dnf install -y smartmontools

# Query drive information
sudo smartctl -i $dev &>/tmp/drive-insight.tmp

# e.g.
# Model Family:     Seagate Barracuda 7200.14 (AF)
# Device Model:     ST1000DM003-9YN162
# Serial Number:    W1D0BKVN
# User Capacity:    1,000,204,886,016 bytes [1.00 TB]
# Sector Sizes:     512 bytes logical, 4096 bytes physical
# ATA Version is:   ATA8-ACS T13/1699-D revision 4
# Local Time is:    Tue Apr 30 21:18:09 2024 EDT

dm=$(cat /tmp/drive-insight.tmp | grep 'Device Model' | cut -d ':' -f 2- | sed 's/[^[:alnum:]]/-/g; s/^-*//; s/-*$//')
sn=$(cat /tmp/drive-insight.tmp | grep 'Serial Number' | cut -d ':' -f 2- | sed 's/[^[:alnum:]]/-/g; s/^-*//; s/-*$//')

mountpoints=$(lsblk --output MOUNTPOINTS $dev | grep '/')

# Define logfile
logfile=report_${dm}_${sn}_$(date +%Y%m%d_%H%M%S).log

# Define a list of commands
commands=(
	"uname -a"
	"sudo smartctl -x $dev"
	"sudo fdisk -l $dev"
	"lsblk -p $dev"
	"for mp in \$mountpoints; do df -kh \$mp; ls -la \$mp; done"
)

# Iterate over the list of commands
for cmd in "${commands[@]}"; do
	# Show the command
	echo "$cmd" | tee -a $logfile
	echo ============ | tee -a $logfile

	# Execute the command
	eval "$cmd" 2>&1 | tee -a $logfile

	echo | tee -a $logfile
done

exit 0
