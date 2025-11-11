#!/bin/bash
#uuid=$(uuidgen)
sudo echo "${USER}"
date=$(date '+%Y-%m-%d_%N')
logpath="testlogs"
runpath="${logpath}/${date}"
#since we must run dmesg as root i chown and change perms so that the user can read the file like normal
mkdir -p "${logpath}"
mkdir -p "${runpath}"
#chown -R "${USER}:${USER}" "${logpath}"
#might help diagnose issues with a run
#sudo dmesg > "${runpath}/${date}_pre.log"
sudo dmesg --clear
for i in {1..10}; do
	#iperf3 -k 1 -c 41.226.22.119 -p 9239
	iperf3 -k 1 -c ccasatpi.dyn.wpi.edu
	sudo dmesg > "${runpath}/${date}_${i}.log"
	sleep 32s
	sudo dmesg --clear
	#chmod 666 "${runpath}/${date}_${i}.log"
	#chown -R "${USER}" "${logpath}"
done
