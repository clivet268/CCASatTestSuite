#!/bin/bash

transfersize="400"
senderhost="127.0.0.1"
numruns=1
locrun=0
algorithm="cubic_hspp"
runid="noid"
rangemin=400
rangemax=400
rangestep=100
namestring="reciever"

echowname() {
	echo "[${namestring}]    ${1}"
}

#set -o pipefail

while getopts "n:a:i:t:s:e:" arg; do
	case $arg in
		n) 	
    		numruns=$OPTARG
    		echo "${OPTARG}"
    		;;
		a)
			algorithm=$OPTARG
			echowname "Using the ${algorithm} algorithm"
			;;
		i)
			runid=$OPTARG
			echowname "Run ID ${runid}"
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
			echowname "Run ID ${runid}"
			;;
		s)
			senderhost=$OPTARG
			#ping?
			;;	
		e)
			IFS='@'
      		read -ra extractstring <<< "$OPTARG"
			extractuser=${extractstring[0]}
			extractip=${extractstring[1]}
			;;
		*)
	    	echowname "One or more flags not understood"
	esac
done

echowname "receiving ${numruns} time(s)..."
for ((i=1; i<=${numruns}; i++)); do
	iperf3 -4 -n "${transfersize}K" -c ${senderhost}
	sleep 14
done
