#!/bin/bash

transfersize=""
senderhost="127.0.0.1"
numruns=1
locrun=0
algorithm="cubic_hspp"
runid="noid"
rangemin=400
rangemax=400
rangestep=100
namestring="reciever"
bindaddr="0.0.0.0"
time=""

echowname() {
	echo "[${namestring}]    ${1}"
}

#set -o pipefail

while getopts "n:a:i:r:s:e:t:B:" arg; do
	case $arg in
		a)
			algorithm=$OPTARG
			echowname "Using the ${algorithm} algorithm"
			;;
		B) 	
			echowname "binding to : ${OPTARG}"
    		bindaddr=$OPTARG
    		;;
		e)
			IFS='@'
      		read -ra extractstring <<< "$OPTARG"
			extractuser=${extractstring[0]}
			extractip=${extractstring[1]}
			IFS=' '
			finalextract=" -e ${extractuser}@${extractip}"
			;;
		i)
			runid=$OPTARG
			echowname "Run ID ${runid}"
			;;
		n) 	
    		numruns=$OPTARG
    		echo "${OPTARG}"
    		;;
		r)
			if [[ ${time} != "" ]]; then
				echowname "-t time and -r range are exclusive, please omit -t if you want to use a size range"
				transfersize=""
      		else
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
			fi
			;;
		s)
			senderhost=$OPTARG
			#ping?
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
	echowname "Cleaning up..."
	pkill iperf3
	exit
}

trap rmlock SIGINT
trap rmlock SIGTERM



sudo sysctl -w net.ipv4.tcp_window_scaling = 1
sudo sysctl -w net.ipv4.tcp_rmem="26214400	26214400	26214400"
sudo sysctl -w net.ipv4.tcp_wmem="26214400	26214400	26214400"
sudo sysctl -w net.core.rmem_max="26214400"
sudo sysctl -w net.core.wmem_max="26214400"
sudo sysctl -w net.core.rmem_default="26214400"
sudo sysctl -w net.core.wmem_default="26214400"

#need sudo?
#sudo echowname "running as : ${USER}"
echowname "receiving ${numruns} time(s)..."
for ((i=1; i<=${numruns}; i++)); do
	if [[ time != "" ]]; then
		iperf3 -R -B "${bindaddr}" -t "${time}" -c "${senderhost}" -l 1K
	else
		if [[ ${transfersize} = "" ]]; then
			iperf3 -R -B "${bindaddr}" -t 10 -c "${senderhost}" -l 1K
		else
			for (( r = rangemin; r <= (rangemax); r += rangestep )); do
				iperf3 -R -B "${bindaddr}" -n "${transfersize}K" -c "${senderhost}"
			done
		fi
	fi
	sleep 14s
done

echowname "Run ID: ${runid}, complete"
