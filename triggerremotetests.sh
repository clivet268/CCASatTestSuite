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
terminalmode="terminal"
basedir='${HOME}/CCASatTestSuite/'
#gets home of the triggering machine, not the desired ones
#basepath="${HOME}/CCASatTestSuite/"

#set -o pipefail

while getopts "dln:a:i:t:s:r:e:x:y:" arg; do
	case $arg in
    	d) 
    		echo "Running with multiple terminals"
    		terminalmode="desktop"
    		;;
		n) 	
    		numruns=$OPTARG
    		;;
		x) 	
    		senderbind="-B ${OPTARG} "
    		;;
		y) 	
    		recieverbind="-B ${OPTARG} "
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
			IFS=' '
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
			IFS=' '
			#ping?
			;;	
		r)
			IFS='@'
      		read -ra recieverstring <<< "$OPTARG"
			recieveruser=${recieverstring[0]}
			recieverip=${recieverstring[1]}
			IFS=' '
			#ping?
			;;	
		e)
			IFS='@'
      		read -ra extractstring <<< "$OPTARG"
			extractuser=${extractstring[0]}
			extractip=${extractstring[1]}
			IFS=' '
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

# if you setup keyauthentication for ssh this requires only entering sudo password
#  on sender terminal, and entering pass for reciever (maybe)


if [[ ${terminalmode} == "desktop" ]]; then
	sssh="${senderuser}@${senderip}"
	rssh="${recieveruser}@${recieverip}"
	gnome-terminal -vvvv --disable-factory -- sh -c "ssh -tt ${sssh} "\''cd ${HOME}/CCASatTestSuite/; ${HOME}/CCASatTestSuite/senderuntest.sh'\'" -n ${numruns} -t ${rangestring} ${senderbind}; sleep 10" &
	senderpid=$!


	sleep 5s
	read -p "[trigger] Enter to launch reciever terminal"$'\n' </dev/tty

	gnome-terminal -vvvv --disable-factory -- sh -c "ssh -tt ${rssh} "\''cd ${HOME}/CCASatTestSuite/; ${HOME}/CCASatTestSuite/recieverruntest.sh'\'" -n ${numruns} -t ${r} -s ${senderip} ${recieverbind}; sleep 10" &
	recieverpid=$!
else

	sssh="${senderuser}@${senderip}"
	rssh="${recieveruser}@${recieverip}"

	echo "echo senderuntest.sh -n ${numruns} -t ${rangestring} ${senderbind}" | ssh clivet268@127.0.0.1 'cat > ${HOME}/CCASatTestSuite/senderrun'

	
	
	echo "recieverruntest.sh -n ${numruns} -t ${r} -s ${senderip} ${recieverbind}" | ssh clivet268@127.0.0.1 'cat > ${HOME}/CCASatTestSuite/senderrun'
	
	cmdstr="sudo -S echo Sudoing; nohup "\''${HOME}'\'"/CCASatTestSuite/senderuntest.sh -n ${numruns} -t ${rangestring} ${senderbind}1>/dev/null 2>/dev/null &"
	#ssh -tt ${sssh} ${cmdstr}
	senderpid=$!
	#sleep 5s

	cmdstr="sudo -S echo Sudoing; nohup "\''${HOME}'\'"/CCASatTestSuite/recieverruntest.sh -n ${numruns} -t ${r} -s ${senderip} ${recieverbind}1>/dev/null 2>/dev/null &"
	#ssh -tt ${rssh} "bash -c '${cmdstr}'"
	recieverpid=$!
fi


#wait "${recieverpid}"
#kill "${senderpid}"

