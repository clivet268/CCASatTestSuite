#!/bin/bash
numruns=1
locrun=0
#declare -a algorithms=("cubic_hspp")
algorithm="cubic_hspp"
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
time=""
finalextract=""
#gets home of the triggering machine, not the desired ones
#basepath="${HOME}/CCASatTestSuite/"

#set -o pipefail

while getopts "dln:a:i:t:S:r:R:e:x:y:" arg; do
	case $arg in
		a)
      		algorithm=$OPTARG
			echo "Using the algorithm: ${algorithm}"
			;;
    	d)
    		echo "Running with multiple terminals"
    		terminalmode="desktop"
    		;;
		n) 	
    		numruns=$OPTARG
    		;;
		t) 	
    		time=$OPTARG
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
		i)
			runid=$OPTARG
			echo "Run ID ${runid}"
			;;
		r)
      		rangestring="$OPTARG"
			;;
		S)
			#12:15
			IFS='@'
      		read -ra senderstring <<< "$OPTARG"
			senderuser=${senderstring[0]}
			senderip=${senderstring[1]}
			IFS=' '
			#ping?
			;;	
		R)
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
			finalextract=" -e ${extractuser}@${extractip}"
			;;
	  *)
	    echo "One or more flags not understood"
	esac
done

overrideStop=0
teststop() {
	if [[ ${overrideStop} -ge 5 ]]; then
		echo "Force Exiting, no cleanup performed"
  		exit
  	fi
  	overrideStop=$((overrideStop + 1))
	echo
	echo "Stopping tests..."
	echo "Auth to stop sender..."
	ssh -t ${sssh} 'sudo pkill iperf3; sudo pkill -f senderuntest.sh'
	echo "Auth to stop reciever..."
	ssh -t ${rssh} 'sudo pkill iperf3; sudo pkill -f recieverruntest.sh'
	exit
}

trap teststop SIGINT

if [[ "$rangemin" == "$rangemax" ]]; then
  echo "Triggering ${numruns} test(s)..."
else
  echo "Doing $(( ((rangemax + rangestep) - rangemin) / rangestep)) sets of ${numruns} test(s), transfer sizes ranging from ${rangemin}K to ${rangemax}K in steps of ${rangestep}K"
fi

#ping the ips
#ssh and run the commands

#sender must precede receiver during setup

# if you setup keyauthentication for ssh this requires only entering sudo password
#  on sender terminal, and entering pass for reciever (maybe)


#this is outdated as most people will be using the cli only version
#TODO update
if [[ ${terminalmode} == "desktop" ]]; then
	sssh="${senderuser}@${senderip}"
	rssh="${recieveruser}@${recieverip}"
	gnome-terminal -vvvv --disable-factory -- sh -c "ssh -tt ${sssh} "\''cd ${HOME}/CCASatTestSuite/; ${HOME}/CCASatTestSuite/senderuntest.sh'\'" -n ${numruns} -t ${rangestring} ${senderbind}${finalextract}; sleep 10" &
	senderpid=$!


	sleep 5s
	read -p "[trigger] Enter to launch reciever terminal"$'\n' </dev/tty

	gnome-terminal -vvvv --disable-factory -- sh -c "ssh -tt ${rssh} "\''cd ${HOME}/CCASatTestSuite/; ${HOME}/CCASatTestSuite/recieverruntest.sh'\'" -n ${numruns} -t ${r} -s ${senderip} ${recieverbind}${finalextract}; sleep 10" &
	recieverpid=$!
else

	sssh="${senderuser}@${senderip}"
	rssh="${recieveruser}@${recieverip}"
	
	finalrange=""
	finaltime=""
	if [[ ${time} != "" ]]; then
		finaltime="-t ${time} "
	else
		if [[ ${transfersize} = "" ]]; then
			finaltime="-t 10 "
		else
			finalrange="-r ${rangestring} "
		fi
	fi
	
	
	#TODO make nicer the vars all bunched up are flags that might not be present
	#start remote sender
	cmdstr="sudo -E -s bash -c "\'"cd /home/${senderuser}; /home/${senderuser}/CCASatTestSuite/senderuntest.sh -n ${numruns} -a ${algorithm} -i ${runid} ${finaltime}${finalrange}${senderbind}${finalextract}"\'
	
	#echo ${cmdstr}
	ssh ${sssh} "${cmdstr}" &
	
	#wait for sender to get ready
	echo "The sender has been triggered,"
	sleep 6s
	
	#start remote reciever
	#cmdstr="sudo bash -c "\'"setsid nohup /home/${recieveruser}/CCASatTestSuite/recieverruntest.sh -n ${numruns} -t ${r} -s ${senderip} ${recieverbind} >> /home/${recieveruser}/CCASatTestSuite/reciever.out 2>&1 < /dev/null &  sleep 1000; exit"\'
	cmdstr="sudo -E -s bash -c "\'"cd /home/${recieveruser}; /home/${recieveruser}/CCASatTestSuite/recieverruntest.sh -n ${numruns} -a ${algorithm} -i ${runid} ${finaltime}${finalrange} -s ${senderip}${recieverbind}${finalextract}"\'

	#echo ${cmdstr}
	ssh ${rssh} "${cmdstr}"
	
	#echo "This program will try to cleanup the remote after it ends,"
	#echo "do Ctrl-C to kill it now or Ctrl-Z and bg to kill it later"
	#one week timeout before you lose control, should we ever make it timeout???	
	#sleep 604800s
fi

