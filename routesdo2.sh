sudo ip route replace default via 130.215.126.1 dev eth0
sudo ip route replace 192.168.1.0/24 dev eth1 src 192.168.1.133 table nic2
sudo ip route replace default via 192.168.1.1 dev eth1 table nic2

sudo ip rule add from 192.168.1.133 table nic2
