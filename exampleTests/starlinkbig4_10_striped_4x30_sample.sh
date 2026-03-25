testname="starlinkbig4_10_striped_4x30_testnumber"
rmlock() {
	exit
}
reciever="receiveruser@starlink.control.plane" # the ip of your receiver machine's non starlink interface
sender1="senderuser@sender1.test.plane" # the ip of your sender machine's test plane, for us we used all the mlcnets
sender2="senderuser@sender2.test.plane"
sender3="senderuser@sender3.test.plane"
sender4="senderuser@sender4.test.plane"
slocbind="trigger.control.plane"  # the ip that the triggering machine will use to reach out over
                                  #  the test plane (the sender local bind ip)
rlocbind=${slocbind} # usually the same as sender local bind
recieverbind="starlink.test.plane" # whatever your starlink interface's public ip is
iperfport="443" # to bypass some firewall restrictions 443 port was used,
                #  remove it from tests below or set it to 5201 if this is not needed


trap rmlock SIGINT
trap rmlock SIGTERM

for i in {1..30}; do
	echo "Set number : ${i}"
	./../triggerremotetests_holding.sh -S ${sender1} -R ${reciever} -X ${slocbind} -Y ${rlocbind} -y ${recieverbind} -n 1 -t 10 -a cubic_wlog -i ${testname} -p ${iperfport}
	sleep 5
	./../triggerremotetests_holding.sh -S ${sender2} -R ${reciever} -X ${slocbind} -Y ${rlocbind} -y ${recieverbind} -n 1 -t 10 -a cubic_hystart -i ${testname} -p ${iperfport}
	sleep 5
	./../triggerremotetests_holding.sh -S ${sender3} -R ${reciever} -X ${slocbind} -Y ${rlocbind} -y ${recieverbind} -n 1 -t 10 -a cubic_hspp -i ${testname} -p ${iperfport}
	sleep 5
	./../triggerremotetests_holding.sh -S ${sender} -R ${reciever} -X ${slocbind} -Y ${rlocbind} -y ${recieverbind} -n 1 -t 10 -a cubic_search -i ${testname} -p ${iperfport}
	sleep 5
	sleep 40
done


