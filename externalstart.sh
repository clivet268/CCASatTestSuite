#!/bin/bash
# Run ssh {username}@{server} "externalstart.sh" from your machine
if [[ ! -e /usr/sbin/clientruntest ]]; then
	echo "clientruntest not present in sbin!"
	exit
fi
sudo whoami
sudo clientruntest &
exit
