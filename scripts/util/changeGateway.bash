# Flush the gateway and add a new one, echo to let the user know the script is complete
ip route flush 0/0
sudo ip route add default via 192.168.5.1