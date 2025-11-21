#!/bin/bash

numruns=${1}
if [[ "${numruns}" == "" ]]; then
	numruns=10
	#echo "Please run ${0} [the number of runs]"
	#exit
fi

for ((i=1; i<=${numruns}; i++)); do
	iperf3 -c 127.0.0.1
	sleep 14
done
