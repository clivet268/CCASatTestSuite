#!/bin/bash
#sudo visudo 
#
sudo echo "$(whoami)"
# Run ssh {username}@{server} "externalstart.sh" from your machine
#if [[ ! -e /usr/sbin/senderuntest ]]; then
#	echo "senderuntest not present in sbin!"
#	exit
#fi

esig="continue"
if [ ! -f esigs ]; then
	touch esigs; 
fi

if [[ $1 == "" ]]; then
	exit
fi
head -n 1 filename
until [[ esig != "continue" ]]
do
	eval "${HOME}/CCASatTestSuite/${cmd}"
	sudo echo "Scanning"
	sleep 5
done
cmd="$(cat ${HOME}/CCASatTestSuite/$1)"
rm "${HOME}/CCASatTestSuite/$1"
eval "${HOME}/CCASatTestSuite/${cmd}"
exit


#sudo extractlogs
exit
