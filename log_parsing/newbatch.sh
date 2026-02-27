if [[ $1 == "" ]]; then
	echo "Usage : newbatch.sh {target dir} {output dir}"
	exit
fi

outputdir="${PWD}/output"
#echo ${2}
if [[ "${2}" == "" ]]; then
	echo "Defaulting output dir to ${outputdir}"
else 
	outputdir="${PWD}/${2}"
fi


# it would help a lot if parseLogToFramework.py parameters were content agnostic
#  as in you give it a file, it should know what log type it is and process, scale, mark
#  all on its own
#  not needed, its just how our logs are structured, this translation layer works too but 
#  it could be clunky as we try and graph the last few things, especially comparison 
#  graphs
processLog(){ 
	echo "Processing file: ${1}"; 
	filenameout=${1::-4}
	echo "Outputing to ${outputdir}/${filenameout}.txt"
	#echo "explitive : ${outputdir}/$(dirname $1)/${filenameout}.txt"
	if grep -q "[HSPP]" "$1"; then
		python3 parseLogToFramework.py HSPP "${PWD}/${1}" "${outputdir}/$(dirname $1)/${filenameout}.txt" &
	elif grep -q "[CUB]" "$1"; then
		python3 parseLogToFramework.py CUBIC "${PWD}/${1}" "${outputdir}/$(dirname $1)/${filenameout}.txt" &
	elif grep -q "[HS]" "$1"; then
		python3 parseLogToFramework.py HS "${PWD}/${1}" "${outputdir}/$(dirname $1)/${filenameout}.txt" &
	elif grep -q "[SEARCH]" "$1"; then
		python3 parseLogToFramework.py SEARCH "${PWD}/${1}" "${outputdir}/$(dirname $1)/${filenameout}.txt" &
	else
		echo "NO LOG TYPE MARKERS FOUND FOR : ${1}"
	fi
}

export -f processLog
export outputdir
find $1 -type f -name '*.log' -exec bash -c "processLog {}" \;

