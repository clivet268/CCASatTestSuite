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
bindaddr=""
tcpbindaddr=""
time=""
iperfport=""

echowname() {
	echo "[${namestring}]    ${1}"
}

#set -o pipefail

while getopts "n:a:i:r:s:e:t:B:p:" arg; do
	case $arg in
		a)
			algorithm=$OPTARG
			echowname "Using the ${algorithm} algorithm"
			;;
		B) 	
			IFS='@'
    		bindaddr=" -B ${OPTARG}"
    		tcpbindaddr=" and host ${OPTARG}"
			echowname "binding to : ${bindaddr}"
    		;;
		e)
			IFS='@'
      		read -ra extractstring <<< "$OPTARG"
			extractuser=${extractstring[0]}
			extractip=${extractstring[1]}
			IFS=''
			finalextract=" -e ${extractuser}@${extractip}"
			;;
		i)
			runid=$OPTARG
			echowname "Run ID ${runid}"
			;;
		p) 	
    		iperfport=" -p ${OPTARG}"
    		echowname "iperf port : ${iperfport}"
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
IFS=''


rmlock() {
	echo
	echowname "Cleaning up..."
	pkill iperf3
	exit
}

trap rmlock SIGINT
trap rmlock SIGTERM


date=$(date '+%Y-%m-%d-%H-%M-%S-%N')
basepath="${HOME}/CCASatTestSuite/"
#this differs from sender! works better with our striped only usage, much nicer imo
logpath="${basepath}testlogs/${runid}/"
mkdir -p "${logpath}"

sudo sysctl -w net.ipv4.tcp_window_scaling=1
sudo sysctl -w net.ipv4.tcp_rmem="262144000	262144000	262144000"
sudo sysctl -w net.ipv4.tcp_wmem="262144000	262144000	262144000"
sudo sysctl -w net.core.rmem_max="262144000"
sudo sysctl -w net.core.wmem_max="262144000"
sudo sysctl -w net.core.rmem_default="262144000"
sudo sysctl -w net.core.wmem_default="262144000"

#need sudo?
#sudo echowname "running as : ${USER}"
echowname "receiving ${numruns} time(s)..."
echowname "iperf port : ${iperfport}"
for ((i=1; i<=${numruns}; i++)); do
	echowname "sudo tcpdump -i $(ip -br addr show | grep 192.168.1.107 | awk '{print $1}') -w ${logpath}${runid}_${i}.pcap -s 120 -f tcp[tcpflags] & tcp-ack != 0 and port 5201${tcpbindaddr} &"
	sudo tcpdump -i $(ip -br addr show | grep 192.168.1.107 | awk '{print $1}') -w "${logpath}${runid}_${i}.pcap" -s 120 -f "tcp[tcpflags] & tcp-ack != 0 and port 5201${tcpbindaddr}" &
	pcappid=$!
	if [[ time != "" ]]; then
		echowname "iperf3 -c ${senderhost}${bindaddr}${iperfport} -t ${time} -R >> ${logpath}${runid}_${i}.iperflog" 
		cmdstr="iperf3 -c ${senderhost}${bindaddr}${iperfport} -t ${time} -R >> ${logpath}${runid}_${i}.iperflog"
		eval "${cmdstr}"
	else
		##not updated
		if [[ ${transfersize} = "" ]]; then
			iperf3 -c "${senderhost}"${bindaddr}${iperfport} -R -t 10
		else
			for (( r = rangemin; r <= (rangemax); r += rangestep )); do
				iperf3 -c "${senderhost}"${bindaddr}${iperfport} -n "${transfersize}K" -R
			done
		fi
	fi
    sleep 0.5s
    echowname "sudo kill ${pcappid}"
    sudo kill -2 ${pcappid}
	sleep 14s
done

echowname "Run ID: ${runid}, complete"
