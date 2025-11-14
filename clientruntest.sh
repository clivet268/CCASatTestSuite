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
sudo sysctl net.ipv4.tcp_congestion_control >> "${logpath}/${date}.sysconf"
sudo sysctl net.ipv4.tcp_window_scaling >> "${logpath}/${date}.sysconf"
sudo sysctl net.ipv4.tcp_rmem >> "${logpath}/${date}.sysconf"
sudo sysctl net.ipv4.tcp_wmem >> "${logpath}/${date}.sysconf"
sudo sysctl net.core.rmem_max >> "${logpath}/${date}.sysconf"
sudo sysctl net.core.wmem_max >> "${logpath}/${date}.sysconf"
sudo sysctl net.core.rmem_default >> "${logpath}/${date}.sysconf"
sudo sysctl net.core.wmem_default >> "${logpath}/${date}.sysconf"
#run in -R so we dont have to worry about hole punching
#no/less magic numbers/vars, pass them in
for i in {1..10}; do
	#iperf3 -k 1 -c 41.226.22.119 -p 9239
	iperf3 -k 1 -c ccasatpi.dyn.wpi.edu
	sudo dmesg > "${runpath}/${date}_${i}.log"
	sleep 32s
	sudo dmesg --clear
	#chmod 666 "${runpath}/${date}_${i}.log"
	#chown -R "${USER}" "${logpath}"
done
