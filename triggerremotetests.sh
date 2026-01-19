

#!/bin/bash
numruns=1
locrun=0
declare -a algorithms=("cubic_hspp")
runid="noid"
rangestring=400
senderip="127.0.0.1"
senderuser=""
recieverip="127.0.0.1"
senderuser=""
extractip="127.0.0.1"
senderuser=""
ccasattestsuitepath="/home/clivet268/Downloads/KernelLearnel/CCASatTestSuite/"

while getopts "ln:a:i:t:s:r:e:" arg; do
	case $arg in
		n) 	
    		numruns=$OPTARG
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



if [[ "$rangemin" == "$rangemax" ]]; then
  echo "Running ${numruns} test(s)..."
else
  echo "Doing $(( ((rangemax + rangestep) - rangemin) / rangestep)) sets of ${numruns} test(s), transfer sizes ranging from ${rangemin}K to ${rangemax}K in steps of ${rangestep}K"
fi
sudo pkill iperf3

#ping the ips
#ssh and run the commands


#sender must precede receiver during setup
sssh="${senderuser}@${senderip}"
ssh -tt "${sssh}" cd ${ccasattestsuitepath}; ${ccasattestsuitepath}senderuntest.sh -n ${numruns} -t rangestring &
senderpid=$!
sleep 7s

rssh="${recieveruser}@${recieverip}"
ssh -tt "${rssh}" cd ${ccasattestsuitepath}; ${ccasattestsuitepath}recieverruntest.sh -t ${r} -s ${senderip} -n ${numruns} &
recieverpid=$!


wait "${recieverpid}"
kill "${senderpid}"
