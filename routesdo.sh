sudo ip route add default via 192.168.1.1 dev enp9s0 table nic2
sudo ip rule add from 192.168.1.133 table nic2
sudo ip route add default via 130.215.120.1 dev wlp3s0 table nic1
sudo ip rule add from 130.215.120.1 table nic1
