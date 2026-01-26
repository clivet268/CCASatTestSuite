#!/bin/bash

scanfile="${HOME}/CCASatTestSuite/scanfile"
params=""
mode="senderuntest.sh"

while getopts "rs:" arg; do
	case $arg in
		r) 	
    		mode="recieverruntest.sh"
    		;;
		s) 	
    		params=$OPTARG
    		;;
		*)
	    	echowname "One or more flags not understood"
	esac
done


sudo echo "$(whoami)"
# Run ssh {username}@{server} "externalstart.sh" from your machine
#if [[ ! -e /usr/sbin/senderuntest ]]; then
#	echo "senderuntest not present in sbin!"
#	exit
#fi

if [[ ${mode} == "" ]]; then
	exit
fi

#until [ -f ${scanfile} ]
#do
#	sudo echo "Scanning"
#	sleep 5
#done
cmd="$(cat ${HOME}/CCASatTestSuite/${mode} ${params})"
#rm scanfile
eval "${HOME}/CCASatTestSuite/${cmd}"
exit


#sudo extractlogs
exit
