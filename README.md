# DHCP Server (Mininet Lab)

A minimal DHCP server built for a CS 164 Mininet topology. This repo is intentionally small and only includes two Python files.

## Files
- `mytopo.py` — Mininet topology
- `dhserver.py` — Minimal DHCP server (UDP port 67)

## Requirements
- Linux + Mininet
- Python 3
- `dhclient` installed

## How to Run

### 1) Start Mininet
From the directory that contains `mytopo.py`:
```bash
sudo mn --custom mytopo.py --topo mytopo
````

### 2) Configure the network (Mininet CLI)

Run the following commands inside the `mininet>` prompt:

```bash
# Server
server ip address add 10.0.0.10/24 dev server-eth0

# Router 1
router1 sysctl -w net.ipv4.ip_forward=1
router1 ip address add 10.0.0.1/24 dev router1-eth0
router1 ip address add 172.16.0.1/24 dev router1-eth1
router1 iptables -t nat -A POSTROUTING -o router1-eth0 -j MASQUERADE
router1 iptables -P FORWARD ACCEPT

# Router 0
router0 sysctl -w net.ipv4.ip_forward=1
router0 ip address add 172.16.0.2/24 dev router0-eth0
router0 ip address add 192.168.1.1/24 dev router0-eth1
router0 ip route add default via 172.16.0.1
router0 iptables -P FORWARD ACCEPT

# Client
client0 ip address add 192.168.1.100/24 dev client0-eth0
client0 ip route add default via 192.168.1.1
```

### 3) Troubleshooting I tried (iptables NAT flush)

Initially, `client0` could not reach the server. I suspected the NAT rule was not being applied correctly, so I flushed and re-added the NAT table rules:

```bash
router1 iptables -t nat -F
router1 iptables -t nat -A POSTROUTING -o router1-eth0 -j MASQUERADE
router1 iptables -t nat -L POSTROUTING -n -v

client0 ping -c 2 10.0.0.10
```

The NAT rule appeared correctly, but the ping still did not succeed.

### 4) Solution (missing return route)

The fix was adding a return route on `router1` back to the client subnet (`192.168.1.0/24`):

```bash
router1 ip route add 192.168.1.0/24 via 172.16.0.2
client0 ping -c 2 10.0.0.10
```

Expected output:

```text
64 bytes from 10.0.0.10: icmp_seq=1 ttl=62 time=11.1 ms
64 bytes from 10.0.0.10: icmp_seq=2 ttl=62 time=16.9 ms
```

## Run the DHCP Server

Start the DHCP server on the Mininet server host:

```bash
server python3 dhserver.py
```

## Notes

* This is a minimal lab implementation for learning purposes.
* DHCP broadcasts normally do not cross routers without a DHCP relay, so DHCP testing should be done on the same broadcast domain as the DHCP server unless a relay is added.

