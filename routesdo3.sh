sudo ip route replace default via 130.215.248.1 dev enp9s0
sudo ip route replace 10.79.94.0/24 dev wlp3s0 src 10.79.94.142 table nic2
sudo ip route replace default via 10.79.94.134 dev wlp3s0 table nic2

sudo ip rule add from 10.79.94.142 table nic2
