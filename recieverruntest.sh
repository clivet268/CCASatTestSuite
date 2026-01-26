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
		n) 	
    		numruns=$OPTARG
    		echo "${OPTARG}"
    		;;
		B) 	
    		bindaddr=$OPTARG
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
			time=$OPTARG
			echowname "Running for ${time} seconds"
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

#need sudo?
#sudo echowname "running as : ${USER}"
echowname "receiving ${numruns} time(s)..."
for ((i=1; i<=${numruns}; i++)); do
	if [[ time != "" ]]; then
		iperf3 -B "${bindaddr}" -t "${time}" -c "${senderhost}"
	else
		if [[ ${transfersize} = "" ]]; then
			iperf3 -B "${bindaddr}" -c "${senderhost}"
		else
			for (( r = rangemin; r <= (rangemax); r += rangestep )); do
				iperf3 -B "${bindaddr}" -n "${transfersize}K" -c "${senderhost}"
			done
		fi
	fi
	sleep 14
done
