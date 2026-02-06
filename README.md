# CCASatTestSuite
The test suite for the conditions evaluated in the satellite congestion control algorithms MQP at WPI

How to use:

triggerremotetests.sh :
-n [default 1] :
number of runs to do per test^*^

-a [default cubic_hspp] : 
the name of the CA that appears in your sender's kernelmodules folder. 
(should be .../CCASatTestSuite/kernelmodules/[CA name]/[CA name].ko)

-t [default 10]


${finaltime}${finalrange} -s ${senderip}${recieverbind}${finalextract} >> /home/${recieveruser}/CCASatTestSuite/reciever.out 2>&1 < /dev/null & exit"\'




TODO:

- Fix ~0 in framework output for a few values sometimes
- Fix apparent control flow in logs
- Generate comparison graphs
- Shared graphing states for graphing to aid in adding more algos
- Make per-CCA kernel modules -> 4 done
  - Cubic, HyStart, HyStartpp, SEARCH
