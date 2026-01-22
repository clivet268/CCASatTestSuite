#!/bin/bash
numruns=1
locrun=0
declare -a algorithms=("cubic_hspp")
runid="noid"
rangestring=400
senderip="127.0.0.1"
senderuser=""
senderbind=""
recieverip="127.0.0.1"
recieveruser=""
recieverbind=""
extractip="127.0.0.1"
extractuser=""
#gets home of the triggering machine, not the desired ones
#basepath="${HOME}/CCASatTestSuite/"

#set -o pipefail

while getopts "ln:a:i:t:s:r:e:" arg; do
	case $arg in
		n) 	
    		numruns=$OPTARG
    		;;
		x) 	
    		senderbind=$OPTARG
    		;;
		y) 	
    		recieverbind=$OPTARG
    		;;
    	l) 
    		echo "Running in local mode"
    		locrun=1
    		;;
		a)
			IFS=','
      		read -ra algostring <<< "$OPTARG"
			algorithms=algostring
			echo "Using the algorithms: ${algorithm}"
			;;
		i)
			runid=$OPTARG
			echo "Run ID ${runid}"
			;;
		t)
      		rangestring="$OPTARG"
			;;
		s)
			#12:15
			IFS='@'
      		read -ra senderstring <<< "$OPTARG"
			senderuser=${senderstring[0]}
			senderip=${senderstring[1]}
			#ping?
			;;	
		r)
			IFS='@'
      		read -ra recieverstring <<< "$OPTARG"
			recieveruser=${recieverstring[0]}
			recieverip=${recieverstring[1]}
			#ping?
			;;	
		e)
			IFS='@'
      		read -ra extractstring <<< "$OPTARG"
			extractuser=${extractstring[0]}
			extractip=${extractstring[1]}
			;;
	  *)
	    echo "One or more flags not understood"
	esac
done


teststop() {
	echo
	echo "Stopping tests..."
	pkill iperf3 2> /dev/null
	kill "${recieverpid}" 2> /dev/null
	kill "${senderpid}" 2> /dev/null
	exit
}

trap teststop SIGINT

if [[ "$rangemin" == "$rangemax" ]]; then
  echo "Triggering ${numruns} test(s)..."
else
  echo "Doing $(( ((rangemax + rangestep) - rangemin) / rangestep)) sets of ${numruns} test(s), transfer sizes ranging from ${rangemin}K to ${rangemax}K in steps of ${rangestep}K"
fi
sudo pkill iperf3

#ping the ips
#ssh and run the commands


#sender must precede receiver during setup
sssh="${senderuser}@${senderip}"
ssh -tt "${sssh}" cd ${basepath}; ${basepath}senderuntest.sh -n ${numruns} -t ${rangestring} &
senderpid=$!
sleep 7s
rssh="${recieveruser}@${recieverip}"
ssh -tt "${rssh}" cd ${basepath}; ${basepath}recieverruntest.sh -n ${numruns} -t ${r} -s ${senderip}  &
recieverpid=$!


wait "${recieverpid}"
kill "${senderpid}"
