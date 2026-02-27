#!/usr/bin/bash

items=$@
MAX_JOBS=16
export MAX_JOBS
#echo $@

# ff=$(find files/test32/test32/mlcnetc -name "*.log")

job_count=0
readarray -d " " -t NA <<< ${items}
# echo ${NA}
# echo
readarray -d "/" -t NAP <<< ${NA}
TEMP=${NAP[@]:0:${#NAP[@]}-3}
OP=$(python3 -c "path='/'.join('${NA[0]}'.split('/')[0:-3]); print(path)")


for file in ${items[@]}; do
	((job_count++))
	readarray -d "/" -t LSP <<< $file
	# echo "BING" $file
	FN1=${LSP[@]: -1}
	FN=$(echo $FN1 | xargs)
	# echo  out/$OP/$FN.txt
	# exit	
	python3 parseLogToFramework.py HSPP $file out/$OP/$FN.txt &

	if (( job_count >= MAX_JOBS )); then
        wait
        job_count=0
    fi
done

wait

echo "jobs done"
