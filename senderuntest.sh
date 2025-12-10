#!/bin/bash
numruns=10
locrun=0
algorithm="cubic_hspp"
runid="noid"
rangemin=400
rangemax=400
rangestep=100
while getopts "ln:a:i:t:" arg; do
	case $arg in
		n) 	
    		numruns=$OPTARG
    		;;
    	l) 
    		echo "Running in local mode"
    		locrun=1
    		;;
		a)
			algorithm=$OPTARG
			echo "Using the ${algorithm} algorithm"
			;;
		i)
			runid=$OPTARG
			echo "Run ID ${runid}"
			;;
		t)
			#range=("${OPTARG//:/ }")
			IFS=':'
      read -ra range <<< "$OPTARG"
			#echo "range invalid, try format [min(:max)](:step), in Kilobytes, "
			# "=~ ^[0-9]+$" means check if its a number string
			if [[ ${range[0]} =~ ^[0-9]+$ ]]; then
        rangemin=${range[0]}
				rangemax=${range[0]}
      fi
      if [[ ${range[1]} =~ ^[0-9]+$ ]]; then
      	rangemax=${range[1]}
			  if [[ ${range[2]} =~ ^[0-9]+$ ]]; then
				  rangestep=${range[2]}
			  fi
      fi
			echo "Run ID ${runid}"
			;;
	  *)
	    echo "One or more flags not understood"
	esac
done




rmlock() {
	echo
	echo "Removing lock..."
	rm -f "${lockfile}"
	kill "${tailpid}" > /dev/null 2> /dev/null
	kill "${tsharkpid}" > /dev/null 2> /dev/null
	exit
}

trap rmlock SIGINT

#uuid=$(uuidgen)
sudo echo "${USER}"
#https://unix.stackexchange.com/questions/278904/linux-file-hierarchy-whats-the-best-location-to-store-lockfiless
lockfile="/var/lock/testsuite.lock"
while [[ -e $"${lockfile}" ]]; do
	lockpid=$(cat ${lockfile})
	if ps -p ${lockpid} > /dev/null; then
		echo "testsuite locked by ${lockpid}, retrying in 10 seconds..."
		sleep 10s
	else
		echo "Other test not running, overriding lock"
  		rm -f "${lockfile}"
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
basepath=""
logpath="${basepath}testlogs/${runid}/"
runpath="${logpath}${date}"
#Should be at least 5 even for testing
# unless network is 100% your own
sleeptime=5

#since we must run dmesg as root i chown and change perms so that the user can read the file like normal
mkdir -p "${logpath}"
mkdir -p "${runpath}"
#chown -R "${USER}:${USER}" "${logpath}"
#might help diagnose issues with a run
#sudo dmesg > "${runpath}/${date}_pre.log"
#/var/log/kernel.log instead of dmesg

#set these as a part of setup
sudo sysctl -w net.ipv4.tcp_congestion_control="${algorithm}"
sudo sysctl -w net.ipv4.tcp_no_metrics_save=1
if [[ $(sudo sysctl net.ipv4.tcp_congestion_control) != "net.ipv4.tcp_congestion_control = ${algorithm}" ]]; then
	echo "algorithm setting failed"
	rm "${lockfile}"
	exit
fi
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
setdir=""
if [[ "$rangemin" == "$rangemax" ]]; then
  echo "Running ${numruns} test(s)..."
else
  echo "Doing $(( ((rangemax + rangestep) - rangemin) / rangestep)) sets of ${numruns} test(s), transfer sizes ranging from ${rangemin}K to ${rangemax}K in steps of ${rangestep}K"
fi
sudo pkill iperf3
for (( r = rangemin; r <= (rangemax); r += rangestep )); do
  for (( i = 1; i <= numruns; i++ )); do
  	thislogdir="${runpath}/${r}K/"
  	thislog="${date}_${i}_${r}K"
	mkdir -p "${thislogdir}"
  	sleep ${sleeptime}s
    echo "${r}K transfer"
  	#iperf3 -k 1 -c 41.226.22.119 -p 9239
  	#iperf3 -k 1 -c ccasatpi.dyn.wpi.edu
  	#/var/log/kernel.log instead of dmesg
  	tail -f -n 0 /var/log/kern.log >> "${thislogdir}${thislog}.log" &
  	tailpid=$!
  	#sudo tshark -Y "tcp.port==5201" >> ${runpath}/${date}_${i}.tshark.log &
  	# Packet count is written to stderr so to suppress packet counts in terminal
  	#  do 2> /dev/null
  	sudo tshark -s 60 >> "${thislogdir}${thislog}.tsharklog" 2> /dev/null &
  	tsharkpid=$!
  	echo "Waiting for client..."
  	if [[ $locrun == 0 ]]; then
  		iperf3 -n "${r}K" -s -1 >> "${thislogdir}${thislog}.iperflog"
  	else
  		iperf3 -n "${r}K" -c ccasatpi.dyn.wpi.edu >> "${thislogdir}${thislog}.iperflog"
  	fi
  	echo "Complete"
  	sleep 0.1s
  	#chmod 666 "${runpath}/${date}_${i}.log"
  	#chown -R "${USER}" "${logpath}"
  	sudo pkill iperf3
  	kill ${tailpid}
  	sleep 0.5s
  	kill ${tsharkpid}
  	echo "runconf:{" >> "${thislogdir}${thislog}.log"
  	echo "size:${r}K" >> "${thislogdir}${thislog}.log"
  	echo "}" >> "${thislogdir}${thislog}.log"
  done
done
rm "${lockfile}"
