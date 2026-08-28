import socket
import struct

# just a shortcut
CIDR_CACHE = {
    24: "255.255.255.0",
    25: "255.255.255.128",
    30: "255.255.255.252"
}

def cidr_prefix_to_netmask(net_bits):
    host_bits = 32 - int(net_bits)
    netmask = socket.inet_ntoa(struct.pack('!I', (1 << 32) - (1 << host_bits)))
    return netmask

def cidr_prefix_to_wildcard_mask(net_bits):
    host_bits = 32 - int(net_bits)
    netmask = socket.inet_ntoa(struct.pack('!I', (1<<32) - ((1 << 32) - (1 << host_bits)) - 1))
    return netmask

class IPAddress:
    def __init__(self, ip: str, mask_bits: int):
        self.ip_addr = ip
        self.mask = mask_bits

    def get_ip_addr(self) -> str:
        return self.ip_addr

    def get_mask(self) -> str:
        return cidr_prefix_to_netmask(self.mask)

    def get_mask_len(self) -> int:
        return self.mask

    def get_cidr(self) -> str:
        return "{}/{}".format(self.ip_addr, self.mask)

    def get_wildcard_mask(self) -> str:
        return cidr_prefix_to_wildcard_mask(self.mask)


class IPv4Address(IPAddress):
    pass


class IPv6Address(IPAddress):
    pass
