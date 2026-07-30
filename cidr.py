import socket
import struct

def cidr_prefix_to_netmask(net_bits):
    host_bits = 32 - int(net_bits)
    netmask = socket.inet_ntoa(struct.pack('!I', (1 << 32) - (1 << host_bits)))
    return netmask

CIDR = {
    24: "255.255.255.0",
    25: "255.255.255.128",
    30: "255.255.255.252"
}
