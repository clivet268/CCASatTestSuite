#!/bin/bash
sudo echo "$(whoami)"
# Run ssh {username}@{server} "externalstart.sh" from your machine
if [[ ! -e /usr/sbin/senderuntest ]]; then
	echo "senderuntest not present in sbin!"
	exit
fi
sudo whoami
sudo senderuntest
sudo extractlogs
exit
