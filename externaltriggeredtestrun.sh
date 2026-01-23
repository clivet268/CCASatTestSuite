#!/bin/bash
sudo echo "$(whoami)"
# Run ssh {username}@{server} "externalstart.sh" from your machine
#if [[ ! -e /usr/sbin/senderuntest ]]; then
#	echo "senderuntest not present in sbin!"
#	exit
#fi

if [[ $1 == "" ]]; then
	exit
fi

until [ -f ${HOME}/CCASatTestSuite/$1 ]
do
	sudo echo "Scanning"
	sleep 5
done
cmd="$(cat ${HOME}/CCASatTestSuite/$1)"
rm "${HOME}/CCASatTestSuite/$1"
eval "${HOME}/CCASatTestSuite/${cmd}"
exit


#sudo extractlogs
exit
