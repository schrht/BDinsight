#!/bin/bash

# Description:
#   Generate a basic report for the block device.
# Maintainer:
#   Charles Shi <schrht@gmail.com>

show_usage() {
	script_name=$(basename "${BASH_SOURCE[0]}")
	echo "Generate a basic report for the block device."
	echo "Usage:   $script_name <block_device>"
	echo "Example: $script_name /dev/sdx"
}

# Get the git version of this script
git_version=$(git describe --all --long 2>/dev/null) || git_version="git-version-unknown"

# Display usage if no block device is provided
[[ -z $1 ]] && show_usage && exit 1

# Check if the provided argument is a block device
if [[ -b $1 ]]; then
	dev=$1
else
	echo "$1 is not a block device!"
	exit 1
fi

# Install smartmontools if not already installed
if ! type smartctl &>/dev/null; then
	if [[ -x $(command -v dnf) ]]; then
		sudo dnf install -y smartmontools || {
			echo "Error installing smartmontools."
			exit 1
		}
	else
		echo "smartctl not found and package manager not supported. Please install smartmontools manually."
		exit 1
	fi
fi

# Query device information using smartctl
if ! output=$(sudo smartctl -i "$dev"); then
	echo "Error retrieving device information."
	exit 1
fi

# Parsing device information
dm=$(echo "$output" | grep 'Device Model' | cut -d ':' -f 2- | sed 's/[^[:alnum:]]/-/g; s/^-*//; s/-*$//')
sn=$(echo "$output" | grep 'Serial Number' | cut -d ':' -f 2- | sed 's/[^[:alnum:]]/-/g; s/^-*//; s/-*$//')

# Get mount points for the device
# shellcheck disable=SC2034  # Unused variables left for readability
mountpoints=$(lsblk --output MOUNTPOINT "$dev" | grep '/')

# Set name for the report file
rptfile="report_${dm}_${sn}_$(date +%Y%m%d_%H%M%S).log"

# Log the git version to the report file
echo -e "$(basename "${BASH_SOURCE[0]}"): ${git_version}\n" | tee -a "${rptfile}"

# Define a list of commands to include in the report
commands=(
	"uname -a"
	"smartctl --version"
	"fdisk --version"
	"lsblk --version"
	"sudo smartctl -x \$dev; echo \"Return Code = \$?\""
	"sudo smartctl -q errorsonly -A -H -l selftest -l error \$dev; echo \"Return Code = \$?\""
	"sudo fdisk -l \$dev"
	"lsblk -p \$dev"
	"for mp in \$mountpoints; do df -kh \$mp; ls -la \$mp; done"
)

# Iterate over the list of commands and execute them, appending output to the report file
for cmd in "${commands[@]}"; do
	# Display the command being executed
	echo "$ $cmd" | tee -a "${rptfile}"
	echo "----------------" | tee -a "${rptfile}"

	# Execute the command and capture both stdout and stderr, appending output to the report file
	eval "$cmd" 2>&1 | tee -a "${rptfile}"

	# Wrap up each command output in the report
	echo -e "----------------\n" | tee -a "${rptfile}"
done

exit 0
