#!/bin/bash
#we do NOT want it running on its own
#sudo systemctl mask iperf3
numruns=1
locrun=0
algorithm="cubic_hspp"
runid="noid"
rangemin=400
rangemax=400
rangestep=100
namestring="sender"
bindaddr="0.0.0.0"
time=""
extractuser=""
extractip=""

echowname() {
	echo "[${namestring}]    ${1}"
}

#TODO should pipefail?
#set -o pipefail

while getopts "ln:a:e:i:r:t:B:" arg; do
	case $arg in
		a)
			algorithm=$OPTARG
			echowname "Using the ${algorithm} algorithm"
			;;
		B) 	
    		bindaddr=$OPTARG
    		;;
		e)
			IFS='@'
      		read -ra extractstring <<< "$OPTARG"
			extractuser=${extractstring[0]}
			extractip=${extractstring[1]}
			IFS=' '
			echo "Final: ${extractip}"
			;;
		i)
			runid=$OPTARG
			echowname "Run ID ${runid}"
			;;
    l)
    	echowname "Running in local mode"
    	locrun=1
    	;;
		n) 	
    		numruns=$OPTARG
    		;;
		r)
			if [[ ${time} != "" ]]; then
				echowname "-t time and -r range are exclusive, please omit -t if you want to use a size range"
      		else
				time="ranged"
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
			fi
			IFS=' '
			;;
		t)
			time=$OPTARG
			echowname "Running for ${time} seconds"
			;;
	  *)
	    echowname "One or more flags not understood"
	esac
done

rmlock() {
	echo
	echowname "Removing lock..."
	rm -f "${lockfile}"
	kill "${tailpid}" > /dev/null 2> /dev/null
	kill "${tsharkpid}" > /dev/null 2> /dev/null
	pkill iperf3
	exit
}

trap rmlock SIGINT
trap rmlock SIGTERM

#uuid=$(uuidgen)
echowname "Sudoing"
sudo echo "running as : ${USER}"
echowname "from user : ${SUDO_USER}"
#https://unix.stackexchange.com/questions/278904/linux-file-hierarchy-whats-the-best-location-to-store-lockfiless
lockfile="/var/lock/testsuite.lock"
while [[ -e $"${lockfile}" ]]; do
	lockpid=$(cat ${lockfile})
	if ps -p ${lockpid} > /dev/null; then
		echowname "testsuite locked by ${lockpid}, retrying in 10 seconds..."
		sleep 10s
	else
		echowname "Other test not running, overriding lock"
  		rm -f "${lockfile}"
	fi
done

# The lockfile is created in noclobber mode and must contain this program's
#  PID in order for this to work, meaning no race condition
set -o noclobber
echo "${$}" > "${lockfile}"
set +o noclobber
if [[ ! ((-e $"${lockfile}") && ($(cat ${lockfile}) == "${$}")) ]]; then
	echowname "Creation of lockfile failed!"
	exit
fi

date=$(date '+%Y-%m-%d-%s_%N')
basepath="${HOME}/CCASatTestSuite/"
logpath="${basepath}testlogs/${runid}/"
runpath="${logpath}${date}"
kernmodpath="${basepath}kernelmodules/"
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
	echowname "algorithm setting failed, attempting to insmod"
	sudo insmod "${kernmodpath}${algorithm}/${algorithm}.ko"
	sudo sysctl -w net.ipv4.tcp_congestion_control="${algorithm}"
	if [[ $(sudo sysctl net.ipv4.tcp_congestion_control) != "net.ipv4.tcp_congestion_control = ${algorithm}" ]]; then
		echowname "insmod failed, algorithm setting failed"
		rmlock
	fi
fi
sudo sysctl net.ipv4.tcp_congestion_control >> "${logpath}${date}.sysconf"
sudo sysctl net.ipv4.tcp_window_scaling >> "${logpath}${date}.sysconf"
sudo sysctl net.ipv4.tcp_rmem >> "${logpath}${date}.sysconf"
sudo sysctl net.ipv4.tcp_wmem >> "${logpath}${date}.sysconf"
sudo sysctl net.core.rmem_max >> "${logpath}${date}.sysconf"
sudo sysctl net.core.wmem_max >> "${logpath}${date}.sysconf"
sudo sysctl net.core.rmem_default >> "${logpath}${date}.sysconf"
sudo sysctl net.core.wmem_default >> "${logpath}${date}.sysconf"

#no/less magic numbers/vars, pass them in
#use ps for flags that include iperf, then abort and flag
#lookup how to get process id for killing
#/var/log/kernel.log instead of dmesg
setdir=""
if [[ "$rangemin" == "$rangemax" ]]; then
  echowname "Running ${numruns} test(s)..."
else
  echowname "Doing $(( ((rangemax + rangestep) - rangemin) / rangestep)) sets of ${numruns} test(s), transfer sizes ranging from ${rangemin}K to ${rangemax}K in steps of ${rangestep}K"
fi
#sudo pkill iperf3

for (( r = rangemin; r <= (rangemax); r += rangestep )); do
  for (( i = 1; i <= numruns; i++ )); do
    thislogdir="${runpath}/${date}_${r}K/"
    thislog="${date}_${i}_${r}K"
    thislogpath="${thislogdir}${thislog}.log"
    
    configstr=""
    if [[ ${time} == "ranged" ]]; then
    	echowname "${r}K transfer"
    	configstr="-n ${r}K " 
    else
		if [[ ${time} != "" ]]; then
			configstr="-t ${time} "
    		thislogdir="${runpath}/${date}_${time}s/"
    		thislog="${date}_${i}_${time}s"
		else
			configstr="-t 10 "
		fi
    fi
    mkdir -p "${thislogdir}"
    sleep ${sleeptime}s
    #/var/log/kernel.log instead of dmesg
    tail -f -n 1 /var/log/kern.log >> "${thislogpath}" &
    tailpid=$!
    #sudo tshark -Y "tcp.port==5201" >> ${runpath}/${date}_${i}.tshark.log &
    # Packet count is written to stderr so to suppress packet counts in terminal
    #  do 2> /dev/null
    sudo tshark -s 60 >> "${thislogdir}${thislog}.tsharklog" 2> /dev/null &
    tsharkpid=$!
    echowname "Waiting for reciever..."
    
    if [[ $locrun == 0 ]]; then
      # -n is client side only, even if running n reverse
      # --one-off should keep things cleaner
      # in this setup you should be sending, so client in -R
      iperf3 -B "${bindaddr}" -s --one-off >> "${thislogdir}${thislog}.iperflog"
    else
    	#in this setup you should be sending as the
    	iperf3 -B "${bindaddr}" "${configstr}" -c ccasatpi.dyn.wpi.edu >> "${thislogdir}${thislog}.iperflog"
    fi
    echowname "Complete"
    sleep 0.1s
    #sudo pkill iperf3
    kill ${tailpid}
    sleep 0.5s
    kill ${tsharkpid}
    echo "runconf : ${time}" >> "${thislogdir}${thislog}.log"
  done
done

echowname "Run ID: ${runid}, complete"
##TODO extraction not automatic for a few reasons

fi
rm "${lockfile}"
