#!/bin/bash
numruns=${1}
if [[ "${numruns}" == "" ]]; then
	numruns=10
	#echo "Please run ${0} [the number of runs]"
	#exit
fi


rmlock() {
  echo "Removing lock..."
  rm -f "${lockfile}"
  exit
}

trap rmlock SIGINT

#uuid=$(uuidgen)
sudo echo "${USER}"
#https://unix.stackexchange.com/questions/278904/linux-file-hierarchy-whats-the-best-location-to-store-lockfiless
lockfile="/var/lock/testsuite.lock"
while [[ -e $"${lockfile}" ]]; do
	lockpid=$(cat ${lockfile})
	if [[ ! $(ps -p ${lockpid}) ]]; then
		echo "Other test not running, overriding lock"
  		rm -f "${lockfile}"
	else
		echo "testsuite locked, retrying in 10 seconds..."
		sleep 10s
	fi
done

# The lockfile is created in noclobber mode and must contain this program's
#  PID in order for this to work, meaning no race condition
set -o noclobber
echo "${$}" > "${lockfile}"
set +o noclobber
if [[ ! ((-e $"${lockfile}") && ($(cat ${lockfile}) == "${$}")) ]]; then
	echo "Creation of lockfile failed!"
	exit
fi

date=$(date '+%Y-%m-%d-%s_%N')
logpath="testlogs"
runpath="${logpath}/${date}"
#Should be at least 5 even for testing
sleeptime=5

#since we must run dmesg as root i chown and change perms so that the user can read the file like normal
mkdir -p "${logpath}"
mkdir -p "${runpath}"
#chown -R "${USER}:${USER}" "${logpath}"
#might help diagnose issues with a run
#sudo dmesg > "${runpath}/${date}_pre.log"
#/var/log/kernel.log instead of dmesg

#set these as a part of setup
#sudo sysctl net.ipv4.tcp_congestion_control=cubic_hspp
sudo sysctl net.ipv4.tcp_congestion_control >> "${logpath}/${date}.sysconf"
sudo sysctl net.ipv4.tcp_window_scaling >> "${logpath}/${date}.sysconf"
sudo sysctl net.ipv4.tcp_rmem >> "${logpath}/${date}.sysconf"
sudo sysctl net.ipv4.tcp_wmem >> "${logpath}/${date}.sysconf"
sudo sysctl net.core.rmem_max >> "${logpath}/${date}.sysconf"
sudo sysctl net.core.wmem_max >> "${logpath}/${date}.sysconf"
sudo sysctl net.core.rmem_default >> "${logpath}/${date}.sysconf"
sudo sysctl net.core.wmem_default >> "${logpath}/${date}.sysconf"
#gather pcaps, for future reference/debugging
#run in -R so we dont have to worry about hole punching
#no/less magic numbers/vars, pass them in
#use ps for flags that include iperf, then abort and flag
#lookup how to get process id for killing
#/var/log/kernel.log instead of dmesg

echo "Running ${numruns} test(s)..."
for ((i=1; i<=${numruns}; i++)); do
	sleep ${sleeptime}s
	#iperf3 -k 1 -c 41.226.22.119 -p 9239
	#iperf3 -k 1 -c ccasatpi.dyn.wpi.edu
	#/var/log/kernel.log instead of dmesg
	tail -f -n 0 /var/log/kern.log >> ${runpath}/${date}_${i}.log &
	tailpid=$!
	sudo tshark -Y "tcp.port==5201" >> ${runpath}/${date}_${i}.tshark.log &
	tsharkpid=$!
	iperf3 -n 300K -c ccasatpi.dyn.wpi.edu >> ${runpath}/${date}_${i}.iperf.log
	echo "${tailpid}"
	sleep 1s
	#chmod 666 "${runpath}/${date}_${i}.log"
	#chown -R "${USER}" "${logpath}"
	kill ${tailpid}
	kill ${tsharkpid}
done

rm "${lockfile}"
