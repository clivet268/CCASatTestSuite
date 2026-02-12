#!/bin/bash
extractbind=""
extractip="127.0.0.1"
extractuser=""
finalextract=""
srcdir=""
dstdir=""
clean="false"
#gets home of the triggering machine, not the desired ones
#basepath="${HOME}/CCASatTestSuite/"

#set -o pipefail
echo "Meant to be run on the machine that contains the logs"
while getopts "ce:E:s:d:" arg; do
	case $arg in
		c)
			clean="true"
			;;
		E) 	
    		extractbind="-B ${OPTARG} "
    		;;
		e)
			IFS='@'
      		read -ra extractstring <<< "$OPTARG"
			extractuser=${extractstring[0]}
			extractip=${extractstring[1]}
			IFS=' '
			finalextract=" -e ${extractuser}@${extractip}"
			;;
		s) 	
    		srcdir="${OPTARG}"
    		;;
		d)
			dstdir="${OPTARG}"
			;;
	  *)
	    echo "One or more flags not understood"
	esac
done

if [[ ${srcdir} == "" ]]; then
	echo "Source dir not defined"
	exit
fi

if [[ ${dstdir} == "" ]]; then
	echo "Destination dir not defined"
	exit
fi

estop() {
	exit
}

trap estop SIGINT
#lock x axis, for now autoscale, then second pass force the scale for all graphs in second pass
#manual better than fully generalized autoscale
#use glomma/cs? as the client (reciever), our computers/cs? as 3rd party, mlcnet as server (sender)
#single user mode, not relevant to this file

sudo echo extracting..
IFS=''
dstdevice="${extractuser}@${extractip}:"
echo ${dstdevice}
if [[ ${clean} != "true" ]]; then
	rsync --remove-source-files -abviuzP ${srcdir} ${dstdevice}${dstdir}
else
	echo Transfering files and cleaning from source in 10 seconds...
	sleep 10s
	rsync --remove-source-files -abviuzP ${srcdir} ${dstdevice}${dstdir} && sudo rm -r ${srcdir}
fi
