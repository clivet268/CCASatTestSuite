controlplanenexthop="130.215.120.1"
controlplaneinterface="wlp3s0"

testplanenexthop="192.168.1.1"
testplanenetwork="192.168.1.0/24"
testplaneinterface="enp9s0"
testplaneip="192.168.1.133"
testplanetable="nic2"

# you will need to do 
#  sudo nano /etc/iproute2/rt_tables
#  and add the line
#  200     nic2

sudo ip route replace default via ${controlplanenexthop} dev ${controlplaneinterface}
sudo ip route replace ${testplanenetwork} dev ${testplaneinterface} src ${testplaneip} table ${testplanetable}
sudo ip route replace default via ${testplanenexthop} dev ${testplaneinterface} table ${testplanetable}

sudo ip rule add from ${testplaneip} table ${testplanetable}














sudo ip route replace default via 130.215.120.1 dev wlp3s0
sudo ip route replace 192.168.1.0/24 dev enp9s0 src 192.168.1.133 table nic2
sudo ip route replace default via 192.168.1.1 dev enp9s0 table nic2

sudo ip rule add from 192.168.1.133 table nic2
